import os
import html
from config import VibesterConfig
from typing import List, Iterable


def line_break_text(text: str, max_width: int = VibesterConfig.max_line_width) -> List[str]:
    """
    Distributes text into lines with the most even length distribution
    while ensuring no line exceeds max_width.
    """
    n_lines = (len(text) // max_width) + 1
    lines = [[] for _ in range(n_lines)]
    tokens = text.split()

    for token in tokens:
        for i in range(len(lines)):
            if len(" ".join(lines[i] + [token])) <= max_width:
                lines[i].append(token)
                break

    result = []
    for line in lines:
        if len(line) > 0:
            result.append(" ".join(line))

    return result


def render_text_svg(x_mm: float, y_mm: float, s: str, class_: str) -> Iterable[str]:
    """
    Render the artist or title, broken across lines if needed.
    """
    lines = line_break_text(s)
    line_height_mm = 6
    h_mm = line_height_mm * len(lines)

    for i, line in enumerate(lines):
        dy_mm = line_height_mm * (1 + i) - h_mm / 2
        yield (
            f'<text x="{x_mm}" y="{y_mm + dy_mm}" text-anchor="middle" '
            f'class="{class_}">{html.escape(line)}</text>'
        )


def format_str_metadata(text: str) -> str:
    """
    Sets the first letter to capital and the rest to lowercase inside a piece of text.
    """
    result = []
    for token in text.split():
        if token.isupper():
            token = token.lower().capitalize()
        result.append(token)
    if len(result) > 0:
        return " ".join(result)
    return ""


if __name__ == "__main__":
    target_dir = "data/music/Ishkur"
    for filename in os.listdir(target_dir):
        print(filename)
        print("\n".join(line_break_text(filename)))
        print("------------", "\n")
