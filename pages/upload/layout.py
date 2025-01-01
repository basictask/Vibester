import uuid
from dash import html
import dash_uploader as du
import dash_mantine_components as dmc
from components.loading import loading
from config import VibesterConfig


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
                                        du.Upload(
                                            id={"name": "upload", "type": "upload", "page": "music"},
                                            max_files=500,
                                            max_file_size=40,
                                            filetypes=[x.lstrip(".") for x in VibesterConfig.supported_formats],
                                            upload_id=str(uuid.uuid1()),  # Unique session id
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
