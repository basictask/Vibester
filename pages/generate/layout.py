from dash import html, dcc
import dash_ag_grid as dag
from config import VibesterConfig
from dash_iconify import DashIconify
import dash_mantine_components as dmc
from components.buttons import button_big


def get_layout() -> html.Div:
    return html.Div(
        children=[
            dmc.Grid(
                # gutter="0px",
                justify="center",
                align="center",
                children=[
                    dmc.GridCol(
                        span=12,
                        children=[
                            dmc.Center(
                                dmc.Title(
                                    "Generate",
                                    order=2,
                                )
                            )
                        ]
                    ),
                    dmc.GridCol(
                        span=12,
                        children=[
                            dmc.Center(
                                html.Div(
                                    style={"width": f"{4 * VibesterConfig.ui_scale}px", "padding": "100px 0"},
                                    children=[
                                        dcc.Loading(
                                            dag.AgGrid(
                                                id={"name": "music_table", "type": "table", "page": "index"},
                                                className="ag-theme-alpine-dark",
                                                columnSize="responsiveSizeToFit",
                                                columnDefs=[
                                                    {"headerName": x.capitalize(), "field": x}
                                                    for x in VibesterConfig.generate_table_cols
                                                ],
                                                rowData=[],
                                                defaultColDef={"sortable": True, "filter": True, "resizable": True},
                                            )
                                        )
                                    ]
                                )
                            )
                        ]
                    ),
                    dmc.GridCol(
                        span=12,
                        children=[
                            button_big(
                                name="generate_run",
                                page="generate",
                                children=[
                                    DashIconify(
                                        icon="ion:cloud-upload-sharp",
                                        width=100,
                                    )
                                ]
                            )
                        ]
                    ),
                    dmc.GridCol(
                        span=12,
                        children=[
                            dmc.Alert(
                                id={"name": "feedback", "type": "alert", "page": "generate"},
                                withCloseButton=True,
                                variant="outline",
                                hide=True,
                            )
                        ]
                    ),
                    dcc.Store(id={"name": "music_store", "type": "store", "page": "generate"}, data=[])
                ]
            )
        ]
    )
