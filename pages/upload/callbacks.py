import os
import base64
from typing import List
from decorators import robust
from config import VibesterConfig
import dash_mantine_components as dmc
from dash import Input, Output, callback, no_update
from pages.generate.music_utils import is_music_file


@robust
def save_file(name: str, content: str) -> None:
    """
    Decode and store a file uploaded with Plotly Dash.
    """
    data = content.encode("utf8").split(b";base64,")[1]
    with open(os.path.join(VibesterConfig.path_music, name), "wb") as fp:
        fp.write(base64.decodebytes(data))


def register_callbacks():
    @callback(
        Output({"name": "uploaded_files", "type": "div", "page": "upload"}, "children"),
        Input({"name": "upload", "type": "upload", "page": "upload"}, "filename"),
        Input({"name": "upload", "type": "upload", "page": "upload"}, "contents"),
    )
    def update_output(uploaded_filenames: List[str], uploaded_file_contents: List[str]) -> List[dmc.Text]:
        """
        Save uploaded files and regenerate the file list.
        """
        if uploaded_filenames is None or uploaded_file_contents is None:
            return no_update

        uploaded_files = []
        current_files = os.listdir(VibesterConfig.path_music)
        for name, data in zip(uploaded_filenames, uploaded_file_contents):
            if name not in current_files and is_music_file(name):
                save_file(name, data)
                gradient = VibesterConfig.mantine_gradient
            else:
                gradient = VibesterConfig.mantine_gradient_red

            uploaded_files.append(
                dmc.Text(
                    name,
                    variant="gradient",
                    gradient=gradient,
                )
            )

        return uploaded_files
