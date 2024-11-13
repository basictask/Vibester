import dash
from dash_iconify import DashIconify
import dash_mantine_components as dmc
from config import VibesterConfig
from dash import Input, Output, dcc, html, no_update, callback


# Instantiation
app = dash.Dash(__name__)

# Master Layout
app.layout = dmc.MantineProvider(
    forceColorScheme="dark",
    theme={"colorScheme": "dark"},
    children=html.Div(
        style={"padding": "100px", "backgroundColor": "#242424"},
        children=[
            dmc.Center(dmc.Title("Vibester", order=1)),
            html.Div(
                id={"name": "content", "type": "div", "page": "index"},
                style={"padding": "100px", "backgroundColor": "#242424"},
                children=[]
            ),
            dcc.Location(id={"name": "url", "type": "location", "page": "index"}, refresh=False)
        ]
    )
)

def get_layout() -> html.Div:
    """
    Layout for the index page
    """
    return html.Div(
        dmc.Grid(
            gutter="100px",
            justify="center",
            align="center",
            children=[
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
    )


def register_callbacks():
    @app.callback(
        Output({"name": "url", "type": "location", "page": "index"}, "pathname"),
        [
            Input({"name": idx, "type": "button", "page": "index"}, "n_clicks")
            for idx in VibesterConfig.pages_config.index
        ],
        prevent_initial_call=True
    )
    def navigate_to_page(*n_clicks) -> str:
        """
        Updates the location's pathname based on which button is clicked.
        """
        ctx = dash.callback_context  # Get the context of the triggered callback
        if not any(n_clicks) or not ctx.triggered:
            return no_update

        # Identify which button was clicked by using the context
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]
        button_name = eval(button_id)["name"]  # Extract the button index from the ID
        # Return the new path to update dcc.Location's pathname
        return button_name

    @callback(
        Output({"name": "content", "type": "div", "page": "index"}, "children"),
        Input({"name": "url", "type": "location", "page": "index"}, "pathname"),
    )
    def update_content(pathname: str) -> html.Div:
        """
        Updates the layout of the main page based on the buttons clicked
        """
        if pathname in VibesterConfig.pages_config.index:
            return VibesterConfig.pages_config.loc[pathname, "layout"]  # Layout for specific page
        return get_layout()  # Layout for home page


register_callbacks()


if __name__ == "__main__":
    app.run_server(debug=True)
    i = 1
