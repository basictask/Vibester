from typing import List, Optional
from config import VibesterConfig
import dash_mantine_components as dmc
from dash import Output, Input, no_update, callback


def register_callbacks():
    @callback(
        Output({"name": "uploaded_files", "type": "div", "page": "upload"}, "children"),
        Input({"name": "upload", "type": "upload", "page": "music"}, "isCompleted"),
        Input({"name": "upload", "type": "upload", "page": "music"}, "filenames"),
    )
    def update_output(is_completed: Optional[bool], filenames: Optional[List[str]]) -> List[dmc.Text]:
        """
        Save uploaded files and regenerate the file list.
        """
        if not is_completed or not filenames:
            return no_update

        uploaded_files = []
        for name in filenames:
            uploaded_files.append(
                dmc.Text(
                    name,
                    variant="gradient",
                    gradient=VibesterConfig.mantine_gradient_red,
                )
            )

        return uploaded_files
