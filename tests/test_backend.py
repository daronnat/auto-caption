from backend.base import InferenceBackend
from backend.registry import BACKENDS


class TestInferenceBackendABC:
    def test_cannot_instantiate_directly(self):
        import pytest
        with pytest.raises(TypeError):
            InferenceBackend()

    def test_device_info_default(self):
        # Create a minimal concrete subclass to test the default device_info
        class DummyBackend(InferenceBackend):
            def load_model(self, model_id, **kwargs): pass
            def generate_caption(self, image_path, prompt, params): return ""
            def generate_caption_from_text(self, prompt, params): return ""
            def unload_model(self): pass
            def model_name(self): return "dummy"
            def backend_name(self): return "dummy"
            def is_loaded(self): return False

        b = DummyBackend()
        info = b.device_info()
        assert "device" in info
        assert "dtype" in info


class TestRegistry:
    def test_backends_dict_has_entries(self):
        assert len(BACKENDS) >= 2

    def test_transformers_backend_registered(self):
        assert "transformers" in BACKENDS

    def test_llamacpp_backend_registered(self):
        assert "llama.cpp" in BACKENDS

    def test_backend_entries_have_module_and_class(self):
        for name, (module, cls) in BACKENDS.items():
            assert isinstance(module, str)
            assert isinstance(cls, str)
