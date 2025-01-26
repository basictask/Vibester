import dash
from config import VibesterConfig
from dash import Input, Output, callback, no_update


def register_callbacks() -> None:
    @callback(
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
