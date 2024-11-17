from dash import html
import dash_ag_grid as dag
from config import VibesterConfig
from dash_iconify import DashIconify
import dash_mantine_components as dmc
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
                                    style={"width": f"{2 * VibesterConfig.ui_scale}px"},
                                    children=[
                                        dag.AgGrid(
                                            id="example-grid",
                                            className="ag-theme-alpine-dark",
                                            columnSize="responsiveSizeToFit",
                                            columnDefs=[
                                                {"headerName": x.capitalize(), "field": x}
                                                for x in VibesterConfig.generate_table_cols
                                            ],
                                            rowData=[],
                                            defaultColDef={"sortable": True, "filter": True, "resizable": True},
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
                                children=[
                                    DashIconify(
                                        icon="ion:cloud-upload-sharp",
                                        width=100,
                                    )
                                ]
                            )
                        ]
                    )
                ]
            )
        ]
    )
