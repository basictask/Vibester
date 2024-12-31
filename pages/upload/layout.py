from dash import html, dcc
from config import VibesterConfig
from dash_iconify import DashIconify
import dash_mantine_components as dmc
from components.loading import loading


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
                                    "Upload",
                                    order=2
                                )
                            )
                        ]
                    ),
                    dmc.GridCol(
                        span=12,
                        children=[
                            dmc.Center(
                                loading(
                                    name="loading",
                                    page="upload",
                                    children=[
                                        dcc.Upload(
                                            id={"name": "upload", "type": "upload", "page": "upload"},
                                            children=DashIconify(
                                                icon="ion:rocket",
                                                width=100,
                                            ),
                                            style={
                                                "display": "flex",
                                                "justifyContent": "center",
                                                "alignItems": "center",
                                                "width": f"{VibesterConfig.ui_scale}px",
                                                "height": f"{VibesterConfig.ui_scale}px",
                                                "lineHeight": "60px",
                                                "borderWidth": "5px",
                                                "borderStyle": "dashed",
                                                "borderRadius": "5px",
                                                "textAlign": "center",
                                            },
                                            multiple=True,
                                        )
                                    ]
                                )
                            )
                        ]
                    ),
                    dmc.GridCol(
                        span=12,
                        children=[
                            dmc.Center(
                                html.Div(
                                    id={"name": "uploaded_files", "type": "div", "page": "upload"},
                                )
                            )
                        ]
                    )
                ]
            )
        ]
    )
