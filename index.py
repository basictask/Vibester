import os
import init
import dash
import dash_uploader as du
from typing import Optional
from loader import setup_folders
from config import VibesterConfig
from user import User, UserManager
import dash_mantine_components as dmc
from dash import Input, Output, dcc, html
from flask import Flask, send_from_directory, redirect, url_for
from flask_login import LoginManager, login_user, login_required, logout_user, current_user

from pages.generate.music_utils import setup_musicbrainz_client
from pages.play.layout import get_layout as get_layout_play
from pages.index.layout import get_layout as get_layout_index
from pages.login.layout import get_layout as get_layout_login
from pages.upload.layout import get_layout as get_layout_upload
from pages.generate.layout import get_layout as get_layout_generate
from pages.play.callbacks import register_callbacks as register_callbacks_play
from pages.index.callbacks import register_callbacks as register_callbacks_index
from pages.upload.callbacks import register_callbacks as register_callbacks_upload
from pages.generate.callbacks import register_callbacks as register_callbacks_generate


# Load dotenv
init.load_env_file(filepath=".env")

# Flask setup
server = Flask(__name__)
server.secret_key = os.getenv("APP_SERVER_SECRET_KEY")
login_manager = LoginManager()
login_manager.init_app(server)
login_manager.login_view = "login"

# Dash app setup
app = dash.Dash(__name__, server=server)
app.config.suppress_callback_exceptions = True

# Initialize the user manager
user_manager = UserManager(filepath=VibesterConfig.path_user, key=os.getenv("APP_USERS_ENCRYPTION_KEY"))


@login_manager.user_loader
def load_user(username: str) -> Optional[User]:
    if not user_manager.user_exists(username=username):
        return None
    else:
        role = user_manager.get_role(username=username)
        return User(username=username, role=role)


# Flask routes for authentication
@server.route("/login", methods=["GET", "POST"])
def login():
    from flask import request, render_template_string

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if (
            user_manager.user_exists(username=username) and  # User exists
            user_manager.verify_user(username=username, password=password)  # Password verification
        ):
            role = user_manager.get_role(username=username)
            user = User(username=username, role=role)
            login_user(user)
            return redirect(url_for("/"))
        else:
            return "Invalid credentials", 401

    # Simple login form
    return render_template_string(get_layout_login())


@server.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


# Dash Layout
app.layout = dmc.MantineProvider(
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


# Protecting Dash views
@app.callback(
    Output({"name": "content", "type": "div", "page": "index"}, "children"),
    Input({"name": "url", "type": "location", "page": "index"}, "pathname"),
)
def update_content(pathname: str) -> html.Div | dcc.Location:
    """
    Updates the layout of the main page based on the buttons clicked in the main menu
    """
    if not current_user.is_authenticated:
        return dcc.Location(pathname='/login', id='redirect')  # Redirect to /login

    role = user_manager.get_role(current_user.id)
    if pathname == "/play" and role in VibesterConfig.pages_config.loc["/play", "role"]:
        return get_layout_play()
    elif pathname == "/upload" and role in VibesterConfig.pages_config.loc["/upload", "role"]:
        return get_layout_upload()
    elif pathname == "/generate" and role in VibesterConfig.pages_config.loc["/generate", "role"]:
        return get_layout_generate()
    else:
        return get_layout_index(role=role)


# Callback registration from all the pages
register_callbacks_play(app=app)
register_callbacks_index()
register_callbacks_upload()
register_callbacks_generate()


# Configure the musicbrainz api client
setup_musicbrainz_client()


# Define a Flask route to serve music files
@server.route("/music/<filename>")
@login_required
def serve_music(filename):
    return send_from_directory(VibesterConfig.path_music, filename)


# Setup folders that are needed for I/O operations
setup_folders()

# Configure dash-uploader to save files to the path defined in config
du.configure_upload(app, VibesterConfig.path_music)


if __name__ == "__main__":
    app.run_server(
        host="0.0.0.0",
        debug=False,
        dev_tools_ui=False,
        ssl_context=(f"{VibesterConfig.path_cert}/cert.pem", f"{VibesterConfig.path_cert}/key.pem")
    )
