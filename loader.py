import os
import pandas as pd
from decorators import robust
from config import VibesterConfig


@robust
def load_db() -> pd.DataFrame:
    """
    Loads the musical data from the local file system.
    """
    if not os.path.exists(VibesterConfig.path_db):
        df = pd.DataFrame(columns=VibesterConfig.generate_table_cols)
        df.to_pickle(VibesterConfig.path_db)
        print(f"Created {VibesterConfig.path_db}")
    return pd.read_pickle(VibesterConfig.path_db)
