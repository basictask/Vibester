import pandas as pd

class VibesterConfig:

    # Multipage navigation
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

    # UI
    ui_scale = 200
    mantine_gradient = {"from": "teal", "to": "lime", "deg": 105}

    # Fixed lists
    generate_table_cols = ["filename", "artist", "title", "year", "genre", "saved", "hash"]
    supported_formats = [".mp3", ".mp4", ".ogg", ".wav", ".wma", ".m4a"]

    # Fixed locations
    path_db = "data/db.parquet"
    path_music = "data/music"
    path_output = "data/output"

    # PDF generation
    grid = True
    crop_marks = True
    font = "Arial"

    # Other settings
    hash_length = 30
