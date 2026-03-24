import re
import torch
from PIL import Image
from transformers import pipeline

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
        self.pipe = None

    def load_model(self):
        self.pipe = pipeline(
            "image-text-to-text",
            model=MODEL_ID,
            trust_remote_code=True,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            device_map="auto",
        )

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

        result = self.pipe(
            messages,
            max_new_tokens=max_words * 5,
            do_sample=False,
        )

        # pipeline returns [{"generated_text": [..., {"role": "assistant", "content": "..."}]}]
        raw = result[0]["generated_text"][-1]["content"].strip()

        raw = raw.split("\n")[0]
        raw = re.sub(r"[^\w\s\-]", "", raw).strip()

        return apply_style(raw, naming_style)
