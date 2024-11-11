import pages
from pages.play.layout import layout as layout_play
from pages.generate.layout import layout as layout_generate
from pages.filter.layout import layout as layout_filter
import pandas as pd

class VibesterConfig:

    pages_config = pd.DataFrame(
        index=[
            "play",
            "generate",
            "filter",
        ],
        data={
            "icon": [
                "ion:musical-notes",
                "ion:sparkles",
                "ion:filter",
            ],
            "pathname": [
                "/play",
                "/generate",
                "/filter",
            ],
            "layout": [
                pages.play.layout.layout,
                pages.generate.layout.layout,
                pages.filter.layout.layout,
            ]
        }
    )

    ui_scale = 200
    mantine_gradient = {"from": "teal", "to": "lime", "deg": 105}
