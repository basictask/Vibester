import os
from typing import Optional


def find_file(root_dir: str, filename: str, ) -> Optional[str]:
    """
    Search for a file by name in the specified root folder.
    """
    for dirpath, _, filenames in os.walk(root_dir):  # Traverse the directory tree
        if filename in filenames:
            return str(os.path.join(dirpath, filename)).replace("\\", "/")
    return None
