import re

STYLE_INSTRUCTIONS = {
    "camelCase": "Format the filename in camelCase (e.g. myBeautifulPhoto).",
    "snake_case": "Format the filename in snake_case (e.g. my_beautiful_photo).",
    "kebab-case": "Format the filename in kebab-case (e.g. my-beautiful-photo).",
    "Title Case": "Format the filename in Title Case with spaces (e.g. My Beautiful Photo).",
}

STYLE_NAMES = list(STYLE_INSTRUCTIONS.keys())


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
