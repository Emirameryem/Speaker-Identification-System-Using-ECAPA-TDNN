import os
import shutil
from pathlib import Path

def ensure_dir(directory):
    Path(directory).mkdir(parents=True, exist_ok=True)

def list_files(directory, extension=None):
    path = Path(directory)
    if not path.exists():
        return []
    if extension:
        return list(path.glob(f"*.{extension}"))
    return list(path.iterdir())
