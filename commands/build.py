from __future__ import annotations

from zipfile import ZipFile
from pathlib import Path
import subprocess
import shutil
import json
import glob
import os

import _click as click

import config


def _return_code(command: str) -> int:
    return subprocess.run(command).returncode


class BuildCommand:

    def __init__(self, dir: Path = None):
        """
        TODOC
        """
        if dir is None:
            dir = Path(".")

        build_infos = self._read_build_infos(dir)

        dependencies = build_infos.get("dependencies", list())
        include = build_infos.get("include", list())
        csproj = build_infos.get("csproj")

        # fmt: off
        self.root_dir = dir
        self.build_infos = build_infos
        self.mod_name = build_infos["name"]
        self.mod_path = build_infos.get("mod_path") or Path(config.PATH_7D2D, "Mods", self.mod_name)

        self.include = [path for path in include]
        self.dependencies = [Path(dir, path) for path in dependencies]

        self.build_zip = Path(dir, f"{self.mod_name}.zip")
        self.build_dir = Path(dir, "build")
        # fmt: on

        self.csproj = None
        self.build_cmd = None

        if csproj is not None:
            self.csproj = Path(self.root_dir, csproj)
            self.build_cmd = f"dotnet build --no-incremental {csproj}"

    def _read_build_infos(self, dir: Path) -> dict:
        """
        TODOC
        """
        build_infos = Path(dir, "build.json")

        if not build_infos.exists():
            raise SystemExit("File not found: 'build.json'")

        with open(Path(dir, build_infos), "rb") as reader:
            datas: dict = json.load(reader)

        return datas

    def _include_file(self, path: Path, move: bool = False):

        dst = Path(self.build_dir, path)

        if not dst.parent.exists():
            os.makedirs(dst.parent)

        if move is True:
            shutil.move(path, dst)
        else:
            shutil.copy(path, dst)

    def _include_dir(self, dir_path: Path):
        shutil.copytree(dir_path, Path(self.build_dir, dir_path))

    def _include_glob(self, include: str, move: bool = False):
        """
        TODOC
        """
        for element in glob.glob(include, recursive=True, root_dir=self.root_dir):

            print(f"includes '{element}'")

            path = Path(self.root_dir, element)

            if not path.exists:
                print(f"WARNING path not found: '{path}'")

            if path.is_dir():
                self._include_dir(path)
            else:
                self._include_file(path, move)

    def _add_includes(self):
        """
        TODOC
        """
        for include in self.include:
            self._include_glob(include)

    def _clear_world(
        self,
        world_name: str,
        save_name: str = "Caves",
        hard: bool = False,
    ):

        world_dir = Path(config.PATH_7D2D_USER, f"GeneratedWorlds/{world_name}")
        save_dir = Path(config.PATH_7D2D_USER, f"Saves/{world_name}/{save_name}")

        shutil.rmtree(Path(save_dir, "Region"), ignore_errors=True)
        shutil.rmtree(Path(save_dir, "DynamicMeshes"), ignore_errors=True)
        shutil.rmtree(Path(save_dir, "decoration.7dt"), ignore_errors=True)

        if hard:
            shutil.rmtree(world_dir)

    def _compile_csproj(self) -> bool:

        if self.build_cmd is None:
            return True

        return _return_code(self.build_cmd) == 0

    def build(self):

        if not self._compile_csproj():
            raise SystemExit()

        if self.build_zip.exists():
            os.remove(self.build_zip)

        if self.build_dir.exists():
            shutil.rmtree(self.build_dir)

        os.makedirs(self.build_dir)

        self._add_includes()

        shutil.make_archive(
            base_name=self.mod_name,
            format="zip",
            root_dir=self.build_dir,
        )

        shutil.rmtree(self.build_dir)

    def install(self):

        if self.mod_path.exists():
            shutil.rmtree(self.mod_path)

        with ZipFile(self.build_zip, "r") as zip_file:
            zip_file.extractall(self.mod_path)

    def start_local(self):

        subprocess.Popen(
            cwd=config.PATH_7D2D,
            executable=config.PATH_7D2D_EXE,
            args=["--noeac"],
        )

        self._clear_world("Old Honihebu County")  # default 2048
        self._clear_world("Old Wosayuwe Valley")  # default 4096

    def start_server(self):
        raise SystemExit("Not Implemented yet")

    def shut_down(self):
        # fmt: off
        subprocess.run("taskkill /IM 7DaysToDie.exe /F", capture_output=True)
        subprocess.run("taskkill /IM 7DaysToDieServer.exe /F", capture_output=True)
        # fmt: on

    def release(self):
        """
        TODOC
        """
        self.build()

        shutil.rmtree(self.build_dir, ignore_errors=True)
        os.makedirs(self.build_dir)

        for path in self.dependencies + [self.build_zip]:
            if not path.exists():
                print(f"Dependency not found: '{path}'")
                continue

            if not path.is_file():
                print(f"Dependency is not a file: '{path}'")
                continue

            dst = Path(self.build_dir, path.stem)

            with ZipFile(path, "r") as zip_file:
                zip_file.extractall(dst)

        shutil.make_archive(f"{self.mod_name}-release", "zip", self.build_dir)


@click.command("build")
def cmd_compile():
    """
    Compile the project in the curren working directory and create a zip archive ready for testing
    """
    BuildCommand().build()


@click.command("start-local")
def cmd_start_local():
    """
    TODOC
    """
    builder = BuildCommand()

    builder.build()
    builder.install()
    builder.shut_down()
    builder.start_local()


@click.command("start-server")
def cmd_start_server():
    """
    TODOC
    """
    BuildCommand().start_server()


@click.command("shut_down")
def cmd_shut_down():
    """
    TODOC
    """
    BuildCommand().shut_down()


@click.command("release")
def cmd_release():
    """
    TODOC
    """
    BuildCommand().release()
