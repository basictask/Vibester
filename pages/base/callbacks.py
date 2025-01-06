from user import UserManager
from config import VibesterConfig
from flask_login import current_user
from dash import Output, Input, dcc, html, callback

from pages.play.layout import get_layout as get_layout_play
from pages.index.layout import get_layout as get_layout_index
from pages.upload.layout import get_layout as get_layout_upload
from pages.generate.layout import get_layout as get_layout_generate


def register_callbacks(user_manager: UserManager) -> None:
    @callback(
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
