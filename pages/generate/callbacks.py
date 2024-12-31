import os
import time
import datetime
import pandas as pd
from loader import load_db
from config import VibesterConfig
from typing import Dict, List, Any
from generator.generate import generate
from dash import Input, Output, State, callback, ctx, no_update
from pages.generate.music_utils import is_music_file, calculate_hash, get_metadata


def register_callbacks() -> None:
    @callback(
        Output({"name": "music_table", "type": "table", "page": "index"}, "rowData"),
        Input({"name": "url", "type": "location", "page": "index"}, "pathname"),
        Input({"name": "music_store", "type": "store", "page": "generate"}, "data"),
    )
    def load_music_table(pathname: str, row_data: List[Dict]) -> List[Dict]:
        """
        Loads music from the local storage and correlates it with music stored in the local db. Only records that are
        present in both of the databases are kept. If the generate button is pressed the records in this table will
        be generated a QR code from.
        """
        if ctx.triggered[0]["prop_id"] == ".":
            # Handle the behavior when triggered by the URL
            if pathname != "/generate":
                return no_update

            df_db = load_db()
            result = pd.DataFrame()

            # Read music from the local storage
            for filename in os.listdir(VibesterConfig.path_music):
                filepath = os.path.abspath(os.path.join(VibesterConfig.path_music, filename))

                if is_music_file(filename) and filename in df_db["filename"].values:  # Music file in database
                    new_row = pd.DataFrame(
                        df_db[df_db["filename"] == filename]
                    ).drop_duplicates(keep="first", subset="filename")

                elif is_music_file(filename) and filename not in df_db["filename"]:  # Music file not in database
                    music_metadata = get_metadata(filepath)  # Download metadata ("artist", "title", "year", "genre")
                    if music_metadata is None:
                        music_metadata = dict()

                    new_row = pd.DataFrame(
                        {
                            "filename": [filename],
                            "artist": [music_metadata.get("artist", None)],
                            "title": [music_metadata.get("title", None)],
                            "year": [music_metadata.get("year", None)],
                            "genre": [music_metadata.get("genre", None)],
                            "saved": [False],
                            "hash": [calculate_hash(filename)],
                        }
                    )

                else:
                    continue

                result = pd.concat([result, new_row], ignore_index=True)
                time.sleep(0.34)  # At most 3 requests per second

            return result.to_dict("records")

        else:
            # Handle behavior when the generate button updates the content of the table
            return row_data

    @callback(
        Output({"name": "music_store", "type": "store", "page": "generate"}, "data"),
        Output({"name": "feedback", "type": "alert", "page": "generate"}, "color"),
        Output({"name": "feedback", "type": "alert", "page": "generate"}, "title"),
        Output({"name": "feedback", "type": "alert", "page": "generate"}, "children"),
        Output({"name": "feedback", "type": "alert", "page": "generate"}, "hide"),
        Input({"name": "generate_run", "type": "button", "page": "generate"}, "n_clicks"),
        State({"name": "music_table", "type": "table", "page": "index"}, "rowData"),
        State({"name": "music_table", "type": "table", "page": "index"}, "virtualRowData"),
    )
    def generate_run(
        n_clicks: int,
        row_data: List[Dict],
        row_data_virtual: List[Dict],
    ) -> tuple[Any | List[Dict], Any | str, Any | str, Any | str, Any | bool]:
        """
        Callback function that defines the behavior for the run button on the generate page.
        The function takes the content of the table on the page and renders all the currently shown rows
        into a pdf file with QR codes that can be cut up using scissors to create the cards.
        """
        if not n_clicks or not row_data or not row_data_virtual or len(row_data) == 0 or len(row_data_virtual) == 0:
            return no_update, no_update, no_update, no_update, no_update

        try:
            # Set up the dataframes
            df = pd.DataFrame(row_data)
            df_virtual = pd.DataFrame(row_data_virtual)
            df_virtual.dropna(inplace=True, subset=["artist", "title", "year"])  # Rows must have these tags
            
            # Mark saved files
            filenames_to_mark = df_virtual["filename"].unique()
            mask = df["filename"].isin(filenames_to_mark) & ~df["saved"]
            df.loc[mask, "saved"] = True

            # Save current Dataframe to parquet
            df.to_parquet(VibesterConfig.path_db)

            # Send virtual files to generator
            output_filename = f"output_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.pdf"
            generate(df=df_virtual, filename=output_filename)

            # Return successful message on the page
            return df.to_dict("records"), "green", "Success", f"Records saved to {output_filename}", False

        except Exception as e:
            return no_update, "red", "Error", f"{e}", False
