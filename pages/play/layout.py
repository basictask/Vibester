from dash import html
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
                    )
                ]
            )
        ]
    )
