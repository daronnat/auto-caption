import re
import torch
from PIL import Image
from backend.base import InferenceBackend
from core.style import apply_style


class TransformersBackend(InferenceBackend):
    def __init__(self):
        self._pipe = None
        self._model_id = ""

    def load_model(self, model_id: str, **kwargs) -> None:
        from transformers import pipeline

        self._model_id = model_id
        self._pipe = pipeline(
            "image-text-to-text",
            model=model_id,
            trust_remote_code=True,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            device_map="auto",
        )

    def generate_caption(self, image_path: str, prompt: str, params: dict) -> str:
        image = Image.open(image_path).convert("RGB")

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image", "image": image},
                    {"type": "text", "text": prompt},
                ],
            }
        ]

        return self._run(messages, params)

    def generate_caption_from_text(self, prompt: str, params: dict) -> str:
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                ],
            }
        ]

        return self._run(messages, params)

    def _run(self, messages: list, params: dict) -> str:
        gen_kwargs = {
            "max_new_tokens": params.get("max_new_tokens", 50),
            "do_sample": params.get("temperature", 0) > 0,
        }
        if gen_kwargs["do_sample"]:
            gen_kwargs["temperature"] = params["temperature"]
            gen_kwargs["top_p"] = params.get("top_p", 1.0)

        result = self._pipe(messages, **gen_kwargs)
        raw = result[0]["generated_text"][-1]["content"].strip()

        raw = raw.split("\n")[0]
        raw = re.sub(r"[^\w\s\-]", "", raw).strip()

        naming_style = params.get("naming_style", "snake_case")
        return apply_style(raw, naming_style)

    def unload_model(self) -> None:
        if self._pipe is not None:
            del self._pipe
            self._pipe = None
            if torch.cuda.is_available():
                torch.cuda.empty_cache()

    def model_name(self) -> str:
        return self._model_id or "None"

    def backend_name(self) -> str:
        return "transformers"

    def is_loaded(self) -> bool:
        return self._pipe is not None
