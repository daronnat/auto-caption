import re
import torch
from PIL import Image
from transformers import AutoProcessor

MODEL_ID = "Qwen/Qwen3.5-0.8B"

STYLE_INSTRUCTIONS = {
    "camelCase": "Format the filename in camelCase (e.g. myBeautifulPhoto).",
    "snake_case": "Format the filename in snake_case (e.g. my_beautiful_photo).",
    "kebab-case": "Format the filename in kebab-case (e.g. my-beautiful-photo).",
    "Title Case": "Format the filename in Title Case with spaces (e.g. My Beautiful Photo).",
}


def apply_style(text: str, style: str) -> str:
    words = re.split(r"[\s_\-]+", text.strip())
    words = [w for w in words if w]
    if not words:
        return "untitled"
    if style == "camelCase":
        return words[0].lower() + "".join(w.capitalize() for w in words[1:])
    elif style == "snake_case":
        return "_".join(w.lower() for w in words)
    elif style == "kebab-case":
        return "-".join(w.lower() for w in words)
    elif style == "Title Case":
        return " ".join(w.capitalize() for w in words)
    return "_".join(w.lower() for w in words)


class ImageRenamer:
    def __init__(self):
        self.model = None
        self.processor = None

    def load_model(self):
        self.processor = AutoProcessor.from_pretrained(MODEL_ID, trust_remote_code=True)

        # Use the VL-specific model class so vision inputs are actually processed.
        # Try Qwen3 VL class first, then Qwen2.5 VL, then fall back to AutoModel.
        dtype = torch.float16 if torch.cuda.is_available() else torch.float32
        load_kwargs = dict(torch_dtype=dtype, device_map="auto", trust_remote_code=True)
        try:
            from transformers import Qwen2_5_VLForConditionalGeneration
            self.model = Qwen2_5_VLForConditionalGeneration.from_pretrained(MODEL_ID, **load_kwargs)
        except (ImportError, Exception):
            from transformers import AutoModel
            self.model = AutoModel.from_pretrained(MODEL_ID, **load_kwargs)

        self.model.eval()

    def generate_filename(
        self,
        image_path: str,
        naming_style: str = "snake_case",
        max_words: int = 5,
        extra_prompt: str = "",
    ) -> str:
        image = Image.open(image_path).convert("RGB")

        prompt_parts = [
            f"Describe this image in {max_words} words or fewer to create a filename.",
            STYLE_INSTRUCTIONS.get(naming_style, ""),
        ]
        if extra_prompt:
            prompt_parts.append(extra_prompt)
        prompt_parts.append(
            "Return ONLY the filename without extension. No explanation, no punctuation, no quotes."
        )
        prompt = " ".join(p for p in prompt_parts if p)

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image", "image": image},
                    {"type": "text", "text": prompt},
                ],
            }
        ]

        # Try qwen_vl_utils for image processing (used by Qwen VL models)
        try:
            from qwen_vl_utils import process_vision_info
            image_inputs, video_inputs = process_vision_info(messages)
        except (ImportError, Exception):
            image_inputs = [image]
            video_inputs = None

        text = self.processor.apply_chat_template(
            messages, tokenize=False, add_generation_prompt=True
        )

        processor_kwargs = dict(text=[text], images=image_inputs, return_tensors="pt")
        if video_inputs:
            processor_kwargs["videos"] = video_inputs

        inputs = self.processor(**processor_kwargs).to(self.model.device)

        max_new_tokens = max_words * 5  # generous budget

        with torch.no_grad():
            output_ids = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                do_sample=False,
            )

        new_tokens = output_ids[0][inputs["input_ids"].shape[1]:]
        raw = self.processor.decode(new_tokens, skip_special_tokens=True).strip()

        # Keep first line only, strip non-alphanumeric except spaces/hyphens/underscores
        raw = raw.split("\n")[0]
        raw = re.sub(r"[^\w\s\-]", "", raw).strip()

        return apply_style(raw, naming_style)
