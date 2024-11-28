import os
import time
import pandas as pd
from loader import load_db
from typing import Dict, List
from config import VibesterConfig
from dash import Input, Output, State, callback, no_update
from music_utils import is_music_file, calculate_md5, get_metadata


def register_callbacks():
    @callback(
        Output({"name": "music_table", "type": "table", "page": "index"}, "rowData"),
        Input({"name": "url", "type": "location", "page": "index"}, "pathname")
    )
    def load_music_table(pathname: str) -> List[Dict]:
        """
        Loads music from the local storage and correlates it with music stored in the local db. Only records that are
        present in both of the databases are kept. If the generate button is pressed the records in this table will
        be generated a QR code from.
        """
        if pathname != "/generate":
            return no_update

        df_db = load_db()
        result = df_db.copy()

        # Read music from the local storage
        for filename in os.listdir(VibesterConfig.path_music):
            filepath = os.path.abspath(os.path.join(VibesterConfig.path_music, filename))
            if is_music_file(filename) and filename in df_db["filename"]:
                # Music file in database - append to the results
                new_row = pd.DataFrame(
                    df_db[df_db["filename"] == filename]
                ).drop_duplicates(keep="first", subset="filename")

            elif is_music_file(filename) and filename not in df_db["filename"]:
                # Music file not in database - calculate stuff then append

                # Download metadata ("artist", "title", "year", "genre")
                music_metadata = get_metadata(filepath)
                if music_metadata is None:
                    continue

                new_row = pd.DataFrame(
                    {
                        "filename": [filename],
                        "artist": [music_metadata.get("artist", "")],
                        "title": [music_metadata.get("title", "")],
                        "year": [music_metadata.get("year", "")],
                        "genre": [music_metadata.get("genre", "")],
                        "saved": [False],
                        "md5": [calculate_md5(filename)],
                    }
                )

            else:
                continue

            result = pd.concat([result, new_row], ignore_index=True)
            time.sleep(0.34)  # At most 3 requests per second

        return result.to_dict("records")
