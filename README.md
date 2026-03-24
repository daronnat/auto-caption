> **Work in progress**

# Auto Caption

A local desktop tool that renames image files based on their visual content using a local multimodal LLM (Qwen3.5-0.8B). No data is sent to any remote API.

## Features

- Select individual files or an entire folder
- Rename or copy to an `ai-renamed/` sub-folder
- Customizable naming style: camelCase, snake_case, kebab-case, Title Case
- Adjustable max words and optional freeform instructions

## Requirements

- Python 3.10+
- A GPU is recommended but not required

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python main.py
```

The model (~1.7 GB) will be downloaded from HuggingFace on first run.
