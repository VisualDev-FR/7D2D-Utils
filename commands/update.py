from pathlib import Path
import http.client
import subprocess
import json

import _click as click

_OWNER = "VisualDev-FR"
_REPO_URL = "7D2D-Utils"
_BRANCH = "master"


def _get_latest_commit() -> str | None:
    """
    Retrieves the latest commit SHA from the remote GitHub repository.
    """
    conn = http.client.HTTPSConnection("api.github.com")
    conn.request(
        "GET",
        f"/repos/{_OWNER}/{_REPO_URL}/commits/{_BRANCH}",
        headers={"User-Agent": "Python-Client"},
    )

    response = conn.getresponse()

    if response.status != 200:
        print(f"Error {response.status}: {response.reason}")
        return None

    commit_info = json.loads(response.read())
    conn.close()

    return commit_info["sha"]


def _get_current_commit() -> str:
    """
    Retrieves the latest commit SHA from the local Git repository.
    """
    repo_path = Path(__file__, "../")

    result = subprocess.run(
        ["git", "-C", repo_path, "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    )

    return result.stdout.strip()


def is_up_to_date() -> bool:
    """
    Checks if the local repository is up to date with the latest remote commit.
    """
    current = _get_current_commit()
    latest = _get_latest_commit()

    if current is None or latest is None:
        return True

    return current == latest


@click.command("update")
def cmd_update():
    """
    Fetches the latest version of the project from the remote Git repository.
    """
    subprocess.run(["git", "pull"])
