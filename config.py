# fmt: off

from typing import Union, Optional
from pathlib import Path
import json
import os


_CONFIG_PATH = Path(__file__, "../config.json").resolve()
_README_PATH = Path(__file__, "../README.md").resolve()


with open(_CONFIG_PATH, "rb") as reader:
    config: dict = json.load(reader)


def _try_get_path(name: str, *default: Union[str, Path]) -> Optional[Path]:
    """
    Try to resolve a path from config.json.
    If fails, try to build a path with default arguments.
    If fails again, returns none
    """
    path: Path = None

    if name in config and config[name] is not None:
        path = Path(config[name])

    if path is None or not path.exists():
        path = Path(*default)

    if path is None or not path.exists():
        return None

    return path.resolve()


def _get_path(name: str, *default: Union[str, Path]) -> Path:
    """
    Calls _try_get_path and raise a FileNotFoundError of the file can't be found.
    Else, return the parsed path
    """

    path = _try_get_path(name, *default)

    if path is None or not path.exists():
        raise FileNotFoundError(
            f"{name}: File not found '{path}'.\n"
            f"Configure it from '{_CONFIG_PATH.resolve()}' or from an environement variable"
        )

    return path

def _get_env(name: str) -> str:
    """
    Try to get an environnement variable and raise a systemExit error if not found
    """
    env = os.environ.get(name)

    if env is None:
        raise SystemExit(f"Missing env variable: '{name}', see '{_README_PATH}' for more details.")

    return env


PATH_7D2D = _get_path("PATH_7D2D", _get_env("PATH_7D2D"))
PATH_7D2D_USER = _get_path("PATH_7D2D", _get_env("APPDATA"), "7DaysToDie")
PATH_7D2D_SERVER = _try_get_path("PATH_7D2D_SERVER", PATH_7D2D, "../7 Days to Die Dedicated Server/7DaysToDieServer.exe")
PATH_PREFABS = _get_path("PATH_PREFABS", PATH_7D2D_USER, "LocalPrefabs")
