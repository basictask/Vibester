import os
import musicbrainzngs
from typing import Optional
from config import VibesterConfig
from user import User, UserManager
from pages.login.layout import get_layout as get_layout_login
from flask_login import login_user, login_required, logout_user, LoginManager
from flask import Flask, redirect, url_for, abort, send_file, send_from_directory


def setup_routes(server: Flask, user_manager: UserManager) -> None:
    """
    Sets up routes for the flask server.
    """
    @server.route("/login", methods=["GET", "POST"])
    def login():
        """
        Flask login route.
        """
        from flask import request, render_template_string

        if request.method == "POST":
            username = request.form["username"]
            password = request.form["password"]
            user_exists = user_manager.user_exists(username=username)
            password_correct = user_manager.verify_user(username=username, password=password)

            if user_exists and password_correct:  # Log the user in
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
        """
        Flask logout route.
        Note: You can't actually log out once you are logged in.
        """
        logout_user()
        return redirect(url_for("login"))

    @server.route("/music/<filename>")
    @login_required
    def serve_music(filename: str):
        """
        File serving route from the root directory of the music folder.
        """
        return send_from_directory(VibesterConfig.path_music, filename)

    @server.route('/music/<path:subpath>')
    def serve_music_recursive(subpath: str):
        """
        File serving route from the recursive subdirectories of the music folder.
        """
        file_path = str(os.path.join(VibesterConfig.path_music, subpath))
        if os.path.isfile(file_path):
            return send_file(file_path, mimetype='audio/mpeg')
        else:
            abort(404)


def setup_login(login_manager: LoginManager, user_manager: UserManager) -> None:
    """
    Sets up functions related to log in.
    """
    @login_manager.user_loader
    def load_user(username: str) -> Optional[User]:
        """
        Registers logic that logs in a user onto the login manager.
        """
        if not user_manager.user_exists(username=username):
            return None
        else:
            role = user_manager.get_role(username=username)
            return User(username=username, role=role)


def setup_folder(root_dir: str, dir_to_create: str) -> None:
    """
    Creates a single folder needed for the data loading.
    """
    abs_path_dir = os.path.join(root_dir, dir_to_create)
    if not os.path.exists(abs_path_dir):
        print(f"Successfully created folder {abs_path_dir}")
        os.makedirs(abs_path_dir, exist_ok=True)


def setup_folders(root_dir: str) -> None:
    """
    Creates the folders needed for the data loading.
    """
    setup_folder(root_dir=root_dir, dir_to_create=VibesterConfig.path_music)
    setup_folder(root_dir=root_dir, dir_to_create=VibesterConfig.path_output)
    setup_folder(root_dir=root_dir, dir_to_create=VibesterConfig.path_cert)
    setup_folder(root_dir=root_dir, dir_to_create=os.path.dirname(VibesterConfig.path_db))
    setup_folder(root_dir=root_dir, dir_to_create=os.path.dirname(VibesterConfig.path_user))


def setup_musicbrainz_client() -> None:
    """
    Configures the user agent for the MusicBrainz client.
    The data is read from the .env file. Please contact Daniel for this.
    """
    musicbrainzngs.set_useragent(
        app=os.getenv("APP_NAME"),
        version=os.getenv("APP_VERSION"),
        contact=os.getenv("APP_CONTACT"),
    )
