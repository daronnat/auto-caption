import base64
import re
from pathlib import Path
from backend.base import InferenceBackend
from core.style import apply_style


class LlamaCppBackend(InferenceBackend):
    def __init__(self):
        self._llama = None
        self._chat_handler = None
        self._model_id = ""

    def load_model(self, model_id: str, **kwargs) -> None:
        from llama_cpp import Llama
        from llama_cpp.llama_chat_format import Llava15ChatHandler
        from huggingface_hub import hf_hub_download

        repo = kwargs.get("gguf_repo", "unsloth/Qwen3.5-0.8B-GGUF")
        model_file = kwargs.get("gguf_file", "Qwen3.5-0.8B-Q4_K_M.gguf")
        mmproj_file = kwargs.get("mmproj_file", "Qwen3.5-0.8B-mmproj-f16.gguf")

        model_path = hf_hub_download(repo_id=repo, filename=model_file)
        mmproj_path = hf_hub_download(repo_id=repo, filename=mmproj_file)

        self._model_id = f"{repo}/{model_file}"

        self._chat_handler = Llava15ChatHandler(clip_model_path=mmproj_path)
        self._llama = Llama(
            model_path=model_path,
            chat_handler=self._chat_handler,
            n_ctx=4096,
            n_gpu_layers=-1,
            verbose=False,
        )

    def generate_caption(self, image_path: str, prompt: str, params: dict) -> str:
        img_data = Path(image_path).read_bytes()
        b64 = base64.b64encode(img_data).decode("utf-8")
        ext = Path(image_path).suffix.lower().lstrip(".")
        mime = {"jpg": "jpeg", "jpeg": "jpeg", "png": "png", "gif": "gif",
                "webp": "webp", "bmp": "bmp", "tiff": "tiff", "tif": "tiff"}
        data_uri = f"data:image/{mime.get(ext, 'jpeg')};base64,{b64}"

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": data_uri}},
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
        temperature = params.get("temperature", 0.0)
        response = self._llama.create_chat_completion(
            messages=messages,
            max_tokens=params.get("max_new_tokens", 50),
            temperature=max(temperature, 0.01),
            top_p=params.get("top_p", 1.0),
        )

        raw = response["choices"][0]["message"]["content"].strip()
        raw = raw.split("\n")[0]
        raw = re.sub(r"[^\w\s\-]", "", raw).strip()

        naming_style = params.get("naming_style", "snake_case")
        return apply_style(raw, naming_style)

    def unload_model(self) -> None:
        if self._llama is not None:
            del self._llama
            self._llama = None
        if self._chat_handler is not None:
            del self._chat_handler
            self._chat_handler = None

    def model_name(self) -> str:
        return self._model_id or "None"

    def backend_name(self) -> str:
        return "llama.cpp"

    def is_loaded(self) -> bool:
        return self._llama is not None
