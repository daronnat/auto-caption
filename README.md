> **Work in progress**

# Auto Caption

A local desktop tool that renames image files based on their visual content using a local multimodal LLM ([Qwen3.5-0.8B](https://huggingface.co/Qwen/Qwen3.5-0.8B)). No data is sent to any remote API.

## Features

- Select individual image files or an entire folder
- Rename in place or copy to an `ai-renamed/` sub-folder
- Naming style toggle: camelCase, snake_case, kebab-case, Title Case
- Adjustable max words and optional freeform prompt instructions
- Non-blocking UI — model runs in a background thread

## Requirements

- Python 3.10+
- A GPU is recommended but CPU works too

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python src/main.py
```

The model (~1.7 GB) is downloaded from HuggingFace on first run and cached locally.

## Project structure

```
src/
  main.py       # PySide6 GUI
  worker.py     # Background thread
  inference.py  # Model loading and filename generation
  renamer.py    # File rename / copy logic
data/           # Sample test images
```

# IMPROVEMENT IDEAS
- a UI that sucks less
- enable language switching
- caching as much as possible
- management of downloaded models etc.
- VRAM requirements warning and transparency on its management
- auto detect and compatibility with Apple Silicon, INTEL and AMD GPUs