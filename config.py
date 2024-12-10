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
    fingerprint_conf_threshold = 0.7

    # Video settings
    video_height = 480
    video_width = 360

    # Styles
    default_style_webcam_video = {
        "border-radius": "15px",
        "padding": "0px",
        "border": "3px solid #c9c9c9",
        "width": f"{2 * ui_scale}px"
    }
    default_style_button_big = {
        "height": f"{ui_scale}px",
        "width": f"{ui_scale}px",
        "display": "block",
        "margin": "0 auto",
    }
