from dash import html, dcc
from config import VibesterConfig
import dash_mantine_components as dmc


def get_layout() -> html.Div:
    return html.Div(
        children=[
            dmc.Grid(
                gutter="100px",
                justify="center",
                align="center",
                children=[
                    dmc.GridCol(
                        span=12,
                        children=[
                            dmc.Center(
                                dmc.Title(
                                    "Play",
                                    order=2
                                )
                            )
                        ]
                    ),
                    dmc.GridCol(
                        span=12,
                        children=[
                            dmc.Center(
                                html.Div(
                                    children=[
                                        html.Video(
                                            id="play_video",
                                            autoPlay=True,
                                            style={
                                                "border-radius": "15px",
                                                "padding": "0px",
                                                "border": "3px solid #c9c9c9",
                                            }
                                        ),
                                        html.Img(
                                            id="play_captured_image",
                                            style={"display": "none"}
                                        )
                                    ]
                                )
                            )
                        ]
                    ),
                    dcc.Location(id={"name": "url", "type": "location", "page": "play"}, refresh=False),
                    dcc.Store(id={"name": "image_store", "type": "store", "page": "play"}, data=[])
                ]
            )
        ]
    )
