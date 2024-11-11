import dash
from dash_iconify import DashIconify
import dash_mantine_components as dmc
from config import VibesterConfig
from dash import Input, Output, dcc, html, no_update


# Instantiation
app = dash.Dash(__name__)

# Master Layout
app.layout = dmc.MantineProvider(
    forceColorScheme="dark",
    theme={"colorScheme": "dark"},
    children=html.Div(
        children=[
            html.Div(
                id={"name": "content", "type": "div", "page": "index"},
                style={"padding": "100px", "backgroundColor": "#242424"},
                children=[
                    dmc.Grid(
                        gutter="100px",
                        justify="center",
                        align="center",
                        children=[
                            dmc.GridCol(
                                span=12,
                                children=[dmc.Center(dmc.Title("Vibester", order=1))],
                            )
                        ] + [
                            dmc.GridCol(
                                span=12,
                                children=[
                                    dmc.Button(
                                        children=DashIconify(
                                            icon=VibesterConfig.pages_config.loc[idx, "icon"],
                                            width=100
                                        ),
                                        id={"name": idx, "type": "button", "page": "index"},
                                        variant="gradient",
                                        gradient=VibesterConfig.mantine_gradient,
                                        style={
                                            "height": f"{VibesterConfig.ui_scale}px",
                                            "width": f"{VibesterConfig.ui_scale}px",
                                            "display": "block",
                                            "margin": "0 auto"
                                        },
                                    )
                                ]
                            ) for idx in VibesterConfig.pages_config.index
                        ]
                    )
                ]
            ),
            dcc.Location(id={"name": "url", "type": "location", "page": "index"}, refresh=False)
        ]
    )
)

# Callbacks
@app.callback(
    Output({"name": "content", "type": "div", "page": "index"}, "children"),
    Input({"name": "url", "type": "location", "page": "index"}, "pathname"),
)
def update_content(pathname: str) -> html.Div:
    """
    Updates the layout of the main page based on the buttons clicked
    """
    if pathname in VibesterConfig.pages_config.index:
        return VibesterConfig.pages_config.loc[pathname, "layout"]
    return no_update


if __name__ == "__main__":
    app.run_server(debug=True)
