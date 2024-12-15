import dash
from config import VibesterConfig
from flask import send_from_directory
import dash_mantine_components as dmc
from dash import Input, Output, dcc, html

from pages.generate.music_utils import setup_musicbrainz_client

from pages.play.layout import get_layout as get_layout_play
from pages.index.layout import get_layout as get_layout_index
from pages.upload.layout import get_layout as get_layout_upload
from pages.generate.layout import get_layout as get_layout_generate

from pages.play.callbacks import register_callbacks as register_callbacks_play
from pages.index.callbacks import register_callbacks as register_callbacks_index
from pages.upload.callbacks import register_callbacks as register_callbacks_upload
from pages.generate.callbacks import register_callbacks as register_callbacks_generate


# Instantiation
app = dash.Dash(__name__)
server = app.server


# Master Layout
app.layout = dmc.MantineProvider(
    forceColorScheme="dark",
    theme={"colorScheme": "dark"},
    children=html.Div(
        style={"padding": "100px 0", "backgroundColor": "#242424"},
        children=[
            dmc.Center(dmc.Title("Vibester", order=1)),
            dmc.Center(
                html.Div(
                    id={"name": "content", "type": "div", "page": "index"},
                    style={"padding": "100px 0", "backgroundColor": "#242424"},
                    children=[]
                )
            ),
            # Frontend components not shown in the pages
            dcc.Store(id={"name": "db", "type": "store", "page": "index"}, data=[]),
            dcc.Location(id={"name": "url", "type": "location", "page": "index"}, refresh=False),
        ]
    )
)


# Callback function for navigation
@app.callback(
    Output({"name": "content", "type": "div", "page": "index"}, "children"),
    Input({"name": "url", "type": "location", "page": "index"}, "pathname"),
)
def update_content(pathname: str) -> html.Div:
    """
    Updates the layout of the main page based on the buttons clicked in the main menu
    """
    if pathname == "/play":
        return get_layout_play()
    elif pathname == "/upload":
        return get_layout_upload()
    elif pathname == "/generate":
        return get_layout_generate()
    else:
        return get_layout_index()


# Callback registration from all the pages
register_callbacks_play(app=app)
register_callbacks_index()
register_callbacks_upload()
register_callbacks_generate()


# Configure the musicbrainz api client
setup_musicbrainz_client()


# Define a Flask route to serve music files
@server.route("/music/<filename>")
def serve_music(filename):
    return send_from_directory(VibesterConfig.path_music, filename)


if __name__ == "__main__":
    app.run_server(
        host="0.0.0.0",
        debug=False,
        dev_tools_ui=False,
        ssl_context=("cert/cert.pem", "cert/key.pem")
    )
