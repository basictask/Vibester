from dash import html
from config import VibesterConfig
from dash_iconify import DashIconify
import dash_mantine_components as dmc
from components.buttons import button_big


def get_layout(role: str) -> html.Div:
    """
    Layout for the index page. The role paramater is the role of the user currently logged in to the application.
    Only those buttons (pages) will be available for the user where the role is in the pages_config role section.
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
                            page="index",
                            style={"display": "none"} if role not in VibesterConfig.pages_config.loc[idx, "role"]
                            else None,
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
