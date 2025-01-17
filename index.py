import os
import utils
import dash
from flask import Flask
import dash_uploader as du
from flask_login import LoginManager

from user import UserManager
from config import VibesterConfig
from utils.setup import setup_routes, setup_login, setup_folders

from pages.generate.music_utils import setup_musicbrainz_client
from pages.base.layout import get_layout as get_layout_base
from pages.base.callbacks import register_callbacks as register_callbacks_base
from pages.play.callbacks import register_callbacks as register_callbacks_play
from pages.index.callbacks import register_callbacks as register_callbacks_index
from pages.generate.callbacks import register_callbacks as register_callbacks_generate


# Load dotenv
utils.load_env_file(filepath=".env")

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

# Dash Layout
app.layout = get_layout_base()

# Callback registration from all the pages
register_callbacks_base(user_manager=user_manager)
register_callbacks_play(app=app)
register_callbacks_index()
register_callbacks_generate()

setup_musicbrainz_client()  # Configure the musicbrainz api client
setup_folders(root_dir=os.path.dirname(os.path.abspath(__file__)))  # Setup folders that are needed for I/O operations
setup_login(login_manager=login_manager, user_manager=user_manager)  # Register logic for logging in
setup_routes(server=server, user_manager=user_manager)  # Setup flask routes
du.configure_upload(app, VibesterConfig.path_music, use_upload_id=True)


if __name__ == "__main__":
    app.run_server(
        host="0.0.0.0",
        debug=False,
        dev_tools_ui=False,
        ssl_context=(
            f"{VibesterConfig.path_cert}/cert.pem",
            f"{VibesterConfig.path_cert}/key.pem"
        )
    )
