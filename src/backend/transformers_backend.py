import re

from backend.base import InferenceBackend
from core.style import apply_style


class TransformersBackend(InferenceBackend):
    def __init__(self):
        self._pipe = None
        self._model_id = ""
        self._device = "cpu"
        self._dtype_name = "float32"

    def load_model(self, model_id: str, **kwargs) -> None:
        import torch
        from transformers import pipeline

        self._model_id = model_id
        device, dtype = self._detect_device()

        if device in ("cuda", "auto"):
            # CUDA / ROCm — use accelerate's device_map
            self._pipe = pipeline(
                "image-text-to-text",
                model=model_id,
                trust_remote_code=True,
                torch_dtype=dtype,
                device_map="auto",
            )
            self._device = "cuda"
        else:
            # MPS / XPU / CPU — explicit device
            self._pipe = pipeline(
                "image-text-to-text",
                model=model_id,
                trust_remote_code=True,
                torch_dtype=dtype,
                device=device,
            )
            self._device = device

        self._dtype_name = str(dtype).replace("torch.", "")

    @staticmethod
    def _detect_device() -> tuple:
        """Auto-detect best available compute device and dtype."""
        import torch

        # NVIDIA CUDA or AMD ROCm
        if torch.cuda.is_available():
            return "auto", torch.float16

        # Apple Silicon MPS
        if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
            return "mps", torch.float16

        # Intel XPU (Arc GPUs)
        if hasattr(torch, "xpu") and torch.xpu.is_available():
            return "xpu:0", torch.float16

        return "cpu", torch.float32

    def generate_caption(self, image_path: str, prompt: str, params: dict) -> str:
        from PIL import Image

        image = Image.open(image_path).convert("RGB")
        messages = [{
            "role": "user",
            "content": [
                {"type": "image", "image": image},
                {"type": "text", "text": prompt},
            ],
        }]
        return self._run(messages, params)

    def generate_caption_from_text(self, prompt: str, params: dict) -> str:
        messages = [{
            "role": "user",
            "content": [{"type": "text", "text": prompt}],
        }]
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
            try:
                import torch
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
                elif hasattr(torch, "mps") and hasattr(torch.mps, "empty_cache"):
                    torch.mps.empty_cache()
            except Exception:
                pass

    def model_name(self) -> str:
        return self._model_id or "None"

    def backend_name(self) -> str:
        return "transformers"

    def is_loaded(self) -> bool:
        return self._pipe is not None

    def device_info(self) -> dict:
        return {"device": self._device, "dtype": self._dtype_name}
