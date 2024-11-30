import html
from typing import List, Iterable


def line_break_text(s: str) -> List[str]:
    """
    Line break the artist and title so they (hopefully) fit on a card. This is a
    hack based on string lengths, but it's good enough for most cases.
    """
    if len(s) < 24:
        return [s]

    words = s.split(" ")
    char_count = sum(len(word) for word in words)

    # The starting situation is everything on the first line. We'll try out
    # every possible line break and pick the one with the most even distribution
    # (by characters in the string, not true text width).
    top, bot = " ".join(words), ""
    diff = char_count

    # Try line-breaking between every word.
    for i in range(1, len(words) - 1):
        w1, w2 = words[:i], words[i:]
        t, b = " ".join(w1), " ".join(w2)
        d = abs(len(t) - len(b))
        if d < diff:
            top, bot, diff = t, b, d

    return [top, bot]


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