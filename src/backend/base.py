from abc import ABC, abstractmethod


class InferenceBackend(ABC):
    @abstractmethod
    def load_model(self, model_id: str, **kwargs) -> None:
        ...

    @abstractmethod
    def generate_caption(self, image_path: str, prompt: str, params: dict) -> str:
        """Generate a filename from an image."""
        ...

    @abstractmethod
    def generate_caption_from_text(self, prompt: str, params: dict) -> str:
        """Generate a filename from a text-only prompt (document content embedded in prompt)."""
        ...

    @abstractmethod
    def unload_model(self) -> None:
        ...

    @abstractmethod
    def model_name(self) -> str:
        ...

    @abstractmethod
    def backend_name(self) -> str:
        ...

    @abstractmethod
    def is_loaded(self) -> bool:
        ...
