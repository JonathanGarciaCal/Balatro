from pathlib import Path
from typing import Union


def data_dir() -> Path:
    """Return the top-level data directory path.

    Notebooks can use this helper to locate data files relative to the
    repository root.
    """
    return Path(__file__).resolve().parents[1] / "data"


def load_csv(name: Union[str, Path]):
    import pandas as pd

    path = data_dir() / str(name)
    return pd.read_csv(path)
