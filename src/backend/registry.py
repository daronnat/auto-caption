from backend.base import InferenceBackend

BACKENDS = {
    "transformers": ("backend.transformers_backend", "TransformersBackend"),
    "llama.cpp": ("backend.llamacpp_backend", "LlamaCppBackend"),
}


def available_backends() -> list[str]:
    result = []
    for name, (module, _) in BACKENDS.items():
        try:
            __import__(module)
            result.append(name)
        except ImportError:
            # Check the underlying library instead
            if name == "transformers":
                try:
                    import transformers  # noqa: F401
                    result.append(name)
                except ImportError:
                    pass
            elif name == "llama.cpp":
                try:
                    import llama_cpp  # noqa: F401
                    result.append(name)
                except ImportError:
                    pass
    return result


def get_backend(name: str) -> InferenceBackend:
    if name not in BACKENDS:
        raise ValueError(f"Unknown backend: {name}. Available: {list(BACKENDS.keys())}")

    module_path, class_name = BACKENDS[name]
    import importlib
    mod = importlib.import_module(module_path)
    cls = getattr(mod, class_name)
    return cls()
