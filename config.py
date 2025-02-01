from typing import Union
from pathlib import Path
import json
import os


_CONFIG_PATH = Path(__file__, "../config.json").resolve()
_README_PATH = Path(__file__, "../README.md").resolve()


with open(_CONFIG_PATH, "rb") as reader:
    config: dict = json.load(reader)


def _get_path(name: str, *default: Union[str, Path]) -> Path:
    """
    Try to resolve a path from config.json.
    If fails, try to build a path with default arguments.
    If fails again, raise a SystemExit Error
    """
    path: Path = None

    if name in config and config[name] is not None:
        path = Path(config[name])

    if path is None or not path.exists():
        path = Path(*default)

    if path is None or not path.exists():
        raise SystemExit(
            f"{name}: File not found '{path}'.\n\n"
            "Configure it from '{CONFIG_PATH.resolve()}' or from an environement variable"
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
PATH_7D2D_SERVER = _get_path("PATH_7D2D_SERVER", _get_env("APPDATA"), "7DaysToDie")
PATH_7D2D_EXE = _get_path("PATH_7D2D", PATH_7D2D, "7DaysToDie.exe")
