import dash
from config import VibesterConfig
from dash_iconify import DashIconify
import dash_mantine_components as dmc
from components.buttons import button_big
from dash import Input, Output, dcc, html, no_update, callback

from pages.play.layout import get_layout as get_layout_play
from pages.filter.layout import get_layout as get_layout_filter
from pages.generate.layout import get_layout as get_layout_generate

from pages.play.callbacks import register_callbacks as register_callbacks_play
from pages.filter.callbacks import register_callbacks as register_callbacks_filter
from pages.generate.callbacks import register_callbacks as register_callbacks_generate

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
            dmc.Center(
                html.Div(
                    id={"name": "content", "type": "div", "page": "index"},
                    style={"padding": "100px", "backgroundColor": "#242424"},
                    children=[]
                )
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
                        button_big(
                            name=idx,
                            children=[
                                DashIconify(
                                    icon=VibesterConfig.pages_config.loc[idx, "icon"],
                                    width=100
                                )
                            ]
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
        Updates the layout of the main page based on the buttons clicked in the main menu
        """
        if pathname == "/play":
            return get_layout_play()
        elif pathname == "/filter":
            return get_layout_filter()
        elif pathname == "/generate":
            return get_layout_generate()
        else:
            return get_layout()


# Callback registration from all the pages
register_callbacks()
register_callbacks_play()
register_callbacks_filter()
register_callbacks_generate()

if __name__ == "__main__":
    app.run_server(host="0.0.0.0", debug=True)
    i = 1
