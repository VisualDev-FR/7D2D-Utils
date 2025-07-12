from pathlib import Path
from typing import Optional
import subprocess


def get_commit_hash(repo_path: Path) -> Optional[str]:
    """
    Retrieves the latest commit SHA from the local Git repository.
    """
    if repo_path is None:
        raise ValueError("Null repo_path")

    try:

        result = subprocess.run(
            ["git", "-C", repo_path, "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )

        return result.stdout.strip()

    except Exception:
        return None
