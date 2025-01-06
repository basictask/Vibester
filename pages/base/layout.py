from dash import dcc, html
import dash_mantine_components as dmc


def get_layout() -> dmc.MantineProvider:
    return dmc.MantineProvider(
        forceColorScheme="dark",
        theme={"colorScheme": "dark"},
        children=html.Div(
            style={"padding": "100px 0", "backgroundColor": "#242424"},
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
                                    dmc.Title("Vibester", order=1)
                                )
                            ]
                        ),
                        html.Div(
                            id={"name": "content", "type": "div", "page": "index"},
                            children=[
                                dmc.Text("Log in to continue")
                            ]
                        )
                    ]
                ),
                dcc.Store(id={"name": "db", "type": "store", "page": "index"}, data=[]),
                dcc.Location(id={"name": "url", "type": "location", "page": "index"}, refresh=False),
            ]
        )
    )
