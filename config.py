import pandas as pd

class VibesterConfig:

    pages_config = pd.DataFrame(
        index=[
            "/play",
            "/generate",
            "/filter",
        ],
        data={
            "icon": [
                "ion:musical-notes",
                "ion:sparkles",
                "ion:filter",
            ]
        }
    )

    ui_scale = 200
    mantine_gradient = {"from": "teal", "to": "lime", "deg": 105}

    generate_table_cols = ["filename", "artist", "title", "year", "genre", "saved", "md5"]
    path_db = "data/db.parquet"
    path_music = "data/music"
