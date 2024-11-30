from typing import List
from config import VibesterConfig
import dash_mantine_components as dmc


def button_big(name: str, page: str, children: List = None) -> dmc.Button:
    """
    Note: icon set: https://icon-sets.iconify.design/ion/
    """
    if children is None:
        children = []
    return dmc.Button(
        children=children,
        id={"name": name, "type": "button", "page": page},
        variant="gradient",
        gradient=VibesterConfig.mantine_gradient,
        style={
            "height": f"{VibesterConfig.ui_scale}px",
            "width": f"{VibesterConfig.ui_scale}px",
            "display": "block",
            "margin": "0 auto"
        },
    )
