import os
from dotenv import dotenv_values


def load_env_file(filepath: str) -> None:
    """
    Loads dotenv from the given filepath to the OS environment variables.
    """
    env_vars = dotenv_values(filepath)
    os.environ.update(env_vars)
