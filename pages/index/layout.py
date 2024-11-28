from dash import html
from config import VibesterConfig
from dash_iconify import DashIconify
import dash_mantine_components as dmc
from components.buttons import button_big


def get_layout() -> html.Div:
    """
    Layout for the index page
    """
    return html.Div(
        dmc.Grid(
            gutter="100px",
            justify="center",
            align="center",
            children=[
                dmc.GridCol(
                    span=12,
                    children=[
                        button_big(
                            name=idx,
                            children=[
                                DashIconify(
                                    icon=VibesterConfig.pages_config.loc[idx, "icon"],
                                    width=100
                                )
                            ]
                        )
                    ]
                ) for idx in VibesterConfig.pages_config.index
            ]
        )
    )
