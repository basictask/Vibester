from typing import List, Dict
from config import VibesterConfig
import dash_mantine_components as dmc


def button_big(
    name: str,
    page: str,
    children: List = None,
    style: Dict = None,
    **kwargs
) -> dmc.Button:
    """
    Note: icon set: https://icon-sets.iconify.design/ion/
    """
    if children is None:
        children = []
    if style is None:
        style = VibesterConfig.default_style_button_big
    return dmc.Button(
        children=children,
        id={"name": name, "type": "button", "page": page},
        variant="gradient",
        gradient=VibesterConfig.mantine_gradient,
        style=style,
        **kwargs
    )
