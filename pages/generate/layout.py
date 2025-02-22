from dash import html, dcc
import dash_ag_grid as dag
from config import VibesterConfig
from dash_iconify import DashIconify
import dash_mantine_components as dmc
from components.buttons import button_big
from components.loading import loading


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
                                    style={
                                        "width": "100%",
                                        "padding": "100px 0",
                                        "display": "flex",
                                        "flexDirection": "column",
                                        "flexGrow": 1
                                    },
                                    children=[
                                        loading(
                                            name="loader",
                                            page="generate",
                                            children=[
                                                dag.AgGrid(
                                                    id={"name": "music_table", "type": "table", "page": "index"},
                                                    className="ag-theme-alpine-dark",
                                                    columnSize="responsiveSizeToFit",
                                                    columnDefs=[
                                                        {
                                                            "field": x,
                                                            "headerName": x.capitalize(),
                                                            "tooltipField": x,
                                                            "editable": True,
                                                        }
                                                        for x in VibesterConfig.generate_table_cols
                                                    ],
                                                    rowData=[],
                                                    defaultColDef={
                                                        "sortable": True,
                                                        "filter": True,
                                                        "resizable": True,
                                                        "tooltipComponent": None
                                                    },
                                                    dashGridOptions={
                                                        "enableBrowserTooltips": True
                                                    },
                                                    style={
                                                        "width": "100%",
                                                    }
                                                )
                                            ]
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
                                        icon="ion:document-text",
                                        width=100,
                                    )
                                ]
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
                                        dmc.Alert(
                                            id={"name": "feedback", "type": "alert", "page": "generate"},
                                            variant="outline",
                                            children="",
                                            title="",
                                            color="",
                                            hide=True,
                                            duration=3000,
                                            withCloseButton=True,
                                        )
                                    ]
                                )
                            )
                        ]
                    ),
                    dcc.Download(id={"name": "download", "type": "download", "page": "generate"}),
                    dcc.Store(id={"name": "music_store", "type": "store", "page": "generate"}, data=[])
                ]
            )
        ]
    )
