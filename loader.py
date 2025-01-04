import os
import pandas as pd
from decorators import robust
from config import VibesterConfig


def setup_folders() -> None:
    """
    Creates the folders needed for the data loading.
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))

    abs_path_music = os.path.join(current_dir, VibesterConfig.path_music)
    abs_path_output = os.path.join(current_dir, VibesterConfig.path_output)
    abs_path_cert = os.path.join(current_dir, VibesterConfig.path_cert)
    abs_path_db = os.path.join(current_dir, os.path.dirname(VibesterConfig.path_db))
    abs_path_user = os.path.join(current_dir, os.path.dirname(VibesterConfig.path_user))

    os.makedirs(abs_path_music, exist_ok=True)
    os.makedirs(abs_path_output, exist_ok=True)
    os.makedirs(abs_path_cert, exist_ok=True)
    os.makedirs(abs_path_db, exist_ok=True)
    os.makedirs(abs_path_user, exist_ok=True)


@robust
def load_db() -> pd.DataFrame:
    """
    Loads the musical data from the local file system.
    """
    if not os.path.exists(VibesterConfig.path_db):
        df = pd.DataFrame(columns=VibesterConfig.generate_table_cols)
        df.to_parquet(VibesterConfig.path_db)
    return pd.read_parquet(VibesterConfig.path_db)
