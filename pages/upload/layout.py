import uuid
from dash import html
import dash_uploader as du
from config import VibesterConfig
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
                                        du.Upload(
                                            id={"name": "upload", "type": "upload", "page": "upload"},
                                            max_files=500,
                                            max_file_size=40,
                                            filetypes=[x.lstrip(".") for x in VibesterConfig.supported_formats],
                                            upload_id=str(uuid.uuid1()),  # Unique session id
                                        )
                                    ]
                                )
                            )
                        ]
                    )
                ]
            )
        ]
    )
