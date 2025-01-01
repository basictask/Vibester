import html
from config import VibesterConfig
from generator.track import Track
from typing import List, Literal
from dataclasses import dataclass, field
from generator.generator_utils import render_text_svg


@dataclass
class Table:
    """
    A table of cards laid out on two-sided paper.

    Hitster cards are 65mm wide, so on a 210mm wide A4 paper, we can fit
    3 columns and still have 7mm margin on both sides. That may be a bit
    tight but either way, let's do 3 columns.

    In the 297mm A4 paper, if we put 4 rows of 65mm that leaves 37mm of
    margin, about 20mm top and bottom.
    """
    cells: List[Track] = field(default_factory=list)  # Default to an empty list
    width: int = 3
    height: int = 4

    def append(self, track: Track) -> None:
        self.cells.append(track)

    def is_empty(self) -> bool:
        return len(self.cells) == 0

    def is_full(self) -> bool:
        return len(self.cells) >= self.width * self.height

    def render_svg(self, mode: Literal["qr"] | Literal["title"], page_footer: str) -> str:
        """
        Render the front of the page as svg. The units are in millimeters.
        """
        # Size of the page.
        w_mm = 210
        h_mm = 297
        # Size of the cards / table cells. In the Hitster game I have, the cards
        # have a side length of 65mm. But then fitting the table on A4 paper, it
        # is possible, but the margins get very small to the point where the
        # crop marks may fall into the non-printable region. So make the cards
        # slightly smaller so they are safe to print.
        side_mm = 62

        tw_mm = side_mm * self.width
        th_mm = side_mm * self.height
        hmargin_mm = (w_mm - tw_mm) / 2
        vmargin_mm = hmargin_mm

        parts: List[str] = [
            '<svg version="1.1" width="210mm" height="297mm" '
            'viewBox="0 0 210 297" '
            'xmlns="http://www.w3.org/2000/svg">',
            f"""
                <style>
                text {{ font-family: {VibesterConfig.font!r}; }}
                .year {{ font-size: 18px; font-weight: 900; }}
                .title, .artist, .footer {{ font-size: 5.2px; font-weight: 400; }}
                .title {{ font-style: italic; }}
                rect, line {{ stroke: black; stroke-width: 0.2; }}
                </style>
            """
        ]
        if VibesterConfig.grid:
            parts.append(
                f'<rect x="{hmargin_mm}" y="{vmargin_mm}" '
                f'width="{tw_mm}" height="{th_mm}" '
                'fill="transparent" stroke-linejoin="miter"/>'
            )
        for ix in range(0, self.width + 1):
            x_mm = hmargin_mm + ix * side_mm
            if VibesterConfig.grid and 0 < ix <= self.width:
                parts.append(
                    f'<line x1="{x_mm}" y1="{vmargin_mm}" '
                    f'x2="{x_mm}" y2="{vmargin_mm + th_mm}" />'
                )
            if VibesterConfig.crop_marks:
                parts.append(
                    f'<line x1="{x_mm}" y1="{vmargin_mm - 5}" x2="{x_mm}" y2="{vmargin_mm - 1}" />'
                    f'<line x1="{x_mm}" y1="{vmargin_mm + th_mm + 1}" x2="{x_mm}" y2="{vmargin_mm + th_mm + 5}" />'
                )

        for iy in range(0, self.height + 1):
            y_mm = vmargin_mm + iy * side_mm
            if VibesterConfig.grid and 0 < iy <= self.height:
                parts.append(
                    f'<line x1="{hmargin_mm}" y1="{y_mm}" '
                    f'x2="{hmargin_mm + tw_mm}" y2="{y_mm}" />'
                )
            if VibesterConfig.crop_marks:
                parts.append(
                    f'<line x1="{hmargin_mm - 5}" y1="{y_mm}" x2="{hmargin_mm - 1}" y2="{y_mm}" />'
                    f'<line x1="{hmargin_mm + tw_mm + 1}" y1="{y_mm}" x2="{hmargin_mm + tw_mm + 5}" y2="{y_mm}" />'
                )

        for i, track in enumerate(self.cells):
            if mode == "qr":
                # Note, we mirror over the x-axis, to match the titles codes
                # when printed double-sided.
                ix = self.width - 1 - (i % self.width)
                iy = i // self.width
                qr_path, qr_mm = track.qr_svg()
                # I'm lazy so we center the QR codes, we don't resize them. If the
                # urls get longer, then the QR codes will cover a larger area of the
                # cards.
                x_mm = hmargin_mm + ix * side_mm + (side_mm - qr_mm) / 2
                y_mm = vmargin_mm + iy * side_mm + (side_mm - qr_mm) / 2
                parts.append(f'<g transform="translate({x_mm}, {y_mm})">')
                parts.append(qr_path)
                parts.append(f"</g>")

            if mode == "title":
                ix = i % self.width
                iy = i // self.width
                x_mm = hmargin_mm + (ix + 0.5) * side_mm
                y_mm = vmargin_mm + (iy + 0.5) * side_mm
                parts.append(
                    f'<text x="{x_mm}" y="{y_mm + 6.5}" text-anchor="middle" '
                    f'class="year">{track.year}</text>'
                )
                for part in render_text_svg(x_mm, y_mm - 19, track.artist, "artist"):
                    parts.append(part)
                for part in render_text_svg(x_mm, y_mm + 18, track.title, "title"):
                    parts.append(part)

        parts.append(
            f'<text x="{w_mm - hmargin_mm}" y="{h_mm - hmargin_mm}" text-anchor="end" '
            f'class="footer">{html.escape(page_footer)}</text>'
        )

        parts.append("</svg>")

        return "\n".join(parts)
