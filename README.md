# Auto Caption

A local desktop app that renames image and document files using a local multimodal LLM ([Qwen3.5-0.8B](https://huggingface.co/Qwen/Qwen3.5-0.8B)). No data is sent to any remote API — everything runs on your machine.

## Features

- **Image & document support** — rename images (jpg, png, webp, ...) and documents (pdf, docx, txt, md, html, rst) based on their content
- **Multiple backends** — HuggingFace Transformers (default) or llama.cpp for quantized inference
- **GPU auto-detection** — NVIDIA CUDA, AMD ROCm, Apple Silicon MPS, Intel XPU, with automatic CPU fallback
- **VRAM transparency** — live VRAM usage in the status bar, warnings before loading models that won't fit
- **Inference caching** — results are cached to disk so re-processing the same file is instant
- **Model management** — browse, inspect, and delete downloaded models from the built-in model manager
- **Naming styles** — camelCase, snake_case, kebab-case, Title Case
- **Customizable prompts** — image and document prompt templates with presets, adjustable temperature / top-p / max tokens
- **Output modes** — rename in place or copy to an `ai-renamed/` sub-folder
- **Live language switching** — English / French, no restart needed
- **Dark & light themes** — glassmorphism UI with Catppuccin-based palette
- **Non-blocking UI** — model loading and inference run in background threads

## Requirements

- Python 3.10+
- A GPU is recommended (NVIDIA, AMD, Apple Silicon, or Intel Arc) but CPU works too

## Installation

```bash
# From source
pip install -e .

# Or with optional llama.cpp backend
pip install -e ".[llamacpp]"
```

## Usage

```bash
python src/main.py
```

The model (~1.7 GB) is downloaded from HuggingFace on first run and cached locally.

## Pre-built binaries

Releases include pre-built packages for each platform:

| Platform | Format |
|----------|--------|
| Linux | AppImage |
| Windows | Portable zip (.exe) |
| macOS | .app bundle (zip) |

Download from the [Releases](https://github.com/daronnat/auto-caption/releases) page.

## Project structure

```
src/
  main.py                  # Entry point
  version.py               # Version (single source of truth with pyproject.toml)
  ui/
    main_window.py         # Main GUI window
    theme.py               # Dark/light glassmorphism themes
    prompt_manager.py      # Prompt preset editor
    progress_widget.py     # Progress bar with ETA
    model_manager.py       # Downloaded model browser/deleter
  core/
    config.py              # App config (~/.config/auto-caption/)
    worker.py              # Background rename worker thread
    renamer.py             # File rename/copy with collision handling
    style.py               # Naming style formatting
    text_extract.py        # Document text extraction (txt, md, docx, pdf, html, rst)
    gpu.py                 # GPU detection (CUDA, ROCm, MPS, XPU)
    cache.py               # Inference result cache
    models.py              # HuggingFace model cache management
  backend/
    base.py                # Abstract inference backend
    registry.py            # Backend discovery & factory
    transformers_backend.py  # HuggingFace Transformers backend
    llamacpp_backend.py    # llama.cpp quantized backend
  i18n/
    en.json                # English translations (65 keys)
    fr.json                # French translations (65 keys)
data/                      # Sample test files
```

## CI/CD

- **CI** runs on every push: linting (ruff), i18n validation, version consistency check, import checks on Python 3.10/3.12
- **Releases** are triggered by pushing a `v*` tag — builds run on Linux, Windows, and macOS, then a GitHub Release is created with all artifacts and an auto-generated changelog

```bash
# To release:
# 1. Bump version in pyproject.toml and src/version.py
# 2. Commit, tag, push
git tag v0.1.0
git push origin dev --tags
```

Changelog is generated with [git-cliff](https://git-cliff.org/) from conventional commits.

## License

MIT
