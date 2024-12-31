from dash import html, dcc
from config import VibesterConfig
import dash_mantine_components as dmc
from components.loading import loading
from components.buttons import button_big


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
                                    id={"name": "video", "type": "div", "page": "play"},
                                    children=[
                                        loading(
                                            name="play_loader",
                                            page="play",
                                            children=[

                                            ]
                                        ),
                                        html.Video(
                                            id="play_video",
                                            autoPlay=True,
                                            style={
                                                "border-radius": "15px",
                                                "padding": "0px",
                                                "border": "3px solid #c9c9c9",
                                                "width": f"{2 * VibesterConfig.ui_scale}px"
                                            }
                                        ),
                                        html.Audio(
                                            id={"name": "music", "type": "audio", "page": "play"},
                                            src=f"",
                                            controls=True,
                                            autoPlay=True,
                                            loop=True,
                                            style={"display": "none"}
                                        ),
                                        button_big(
                                            name="stop_music",
                                            page="play",
                                            style={"display": "none"}
                                        )
                                    ]
                                )
                            )
                        ]
                    ),
                    dcc.Location(id={"name": "url", "type": "location", "page": "play"}, refresh=False),
                    dcc.Interval(id={"name": "sample", "type": "interval", "page": "play"}, interval=1000),
                    dcc.Store(id={"name": "music_store", "type": "store", "page": "play"}, data=[]),
                    dcc.Store(id={"name": "frame_store", "type": "store", "page": "play"}, data=[]),
                    dcc.Store(id={"name": "dummy", "type": "store", "page": "play"}, data=[]),
                ]
            )
        ]
    )
