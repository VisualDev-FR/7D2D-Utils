from __future__ import annotations

from zipfile import ZipFile
from pathlib import Path
from typing import List
import subprocess
import shutil
import time
import hashlib
import json
import glob
import os

import _click as click

from . import utils
import config


def _return_code(command: str, quiet: bool = False) -> int:
    return subprocess.run(command, capture_output=quiet).returncode


class SaveCleaningData:

    def __init__(self, world: str, save: str, hard: bool = False):
        self.world  = world
        self.save = save
        self.hard = hard


class ModBuilder:

    def __init__(self, root: Path = None):
        """
        TODOC
        """
        if root is None:
            root = Path(".")

        build_infos = self._read_build_infos(root)

        dependencies = build_infos.get("dependencies", list())
        include = build_infos.get("include", list())
        csproj = build_infos.get("csproj")

        # fmt: off
        self.root_dir = root.resolve()
        self.build_infos = build_infos
        self.mod_name = build_infos["name"]
        self.game_path = Path(build_infos.get("game_path") or config.PATH_7D2D)
        self.mod_path = Path(self.game_path, "Mods", self.mod_name)
        self.prefabs = build_infos.get("prefabs")

        self.include = [path for path in include]
        self.dependencies = [Path(root, path).resolve() for path in dependencies]

        self.zip_archive = Path(root, f"{self.mod_name}.zip").resolve()
        self.build_dir = Path(root, "build").resolve()
        self.save_cleaning_datas = [SaveCleaningData(**data) for data in self.build_infos.get("clear_saves", list())]
        self.commit_hash = utils.get_commit_hash(self.root_dir)
        # fmt: on

        self.csproj = None
        self.build_cmd = None

        if csproj is not None:
            self.csproj = Path(self.root_dir, csproj).resolve()
            self.build_cmd = f'dotnet build --no-incremental "{self.csproj}"'

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

        dst = Path(self.build_dir, path.relative_to(self.root_dir))

        if not dst.parent.exists():
            os.makedirs(dst.parent)

        if move is True:
            shutil.move(path, dst)
        else:
            shutil.copy(path, dst)

    def _include_dir(self, dir_path: Path):

        dst = Path(self.build_dir, dir_path.name)

        shutil.copytree(dir_path, dst)

    def _include_glob(self, include: str, move: bool = False):
        """
        TODOC
        """
        for element in glob.glob(include, recursive=True, root_dir=self.root_dir):

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

    def _clear_save(self, cleaning_datas: SaveCleaningData):
        """
        TODOC
        """
        world_name = cleaning_datas.world
        save_name = cleaning_datas.save

        save_dir = Path(config.PATH_7D2D_USER, f"Saves/{world_name}/{save_name}")

        shutil.rmtree(Path(save_dir, "Region"), ignore_errors=True)
        shutil.rmtree(Path(save_dir, "DynamicMeshes"), ignore_errors=True)
        shutil.rmtree(Path(save_dir, "decoration.7dt"), ignore_errors=True)

        if cleaning_datas.hard:
            shutil.rmtree(save_dir)

    def _clear_saves(self):
        """
        TODOC
        """
        for world_clear_data in self.save_cleaning_datas:
            self._clear_save(world_clear_data)

    def _compile_csproj(self, quiet: bool = False) -> bool:

        if self.build_cmd is None:
            return True

        return _return_code(self.build_cmd, quiet) == 0

    def _build_dependencies(self) -> List[ModBuilder]:

        zip_archives = []

        for dep in self.dependencies:

            build_infos = Path(dep, "build.json")

            if not build_infos.exists():
                raise SystemExit(f"Can't find '{build_infos}'")

            builder = ModBuilder(dep)

            print(f"build {builder.commit_hash[:8]} '{builder.mod_name}' {self._pending_modifications_count(builder.root_dir)}")

            builder.build(quiet=True)

            zip_archives.append(builder)

        return zip_archives

    def _pending_modifications_count(self, repo_path: Path) -> int:
        """
        TODOC
        """
        result = subprocess.check_output(
            "git diff --name-status --staged && git diff --name-status",
            cwd=repo_path,
            shell=True,
        )

        return len(result.decode().split("\n")) - 1

    def _write_version_file(self):
        """
        TODOC
        """
        with open(Path(self.build_dir, "version.txt"), "w") as writer:
            writer.write(self.commit_hash.__str__())

    def _combine_commit_hashes(self, dependencies: List[ModBuilder]) -> str:
        """
        TODOC
        """
        hashes = [dep.commit_hash.__str__() for dep in dependencies]
        hashes.append(self.commit_hash.__str__())
        hashes.sort()

        return hashlib.sha256("".join(hashes).encode()).hexdigest()

    def build(self, clean: bool = False, quiet: bool = False):

        if self.zip_archive.exists():
            os.remove(self.zip_archive)

        if self.build_dir.exists():
            shutil.rmtree(self.build_dir)

        os.makedirs(self.build_dir)

        if not self._compile_csproj(quiet):
            raise SystemExit(f"build failed: {self.mod_name}")

        self._add_includes()
        self._write_version_file()
        self.fetch_prefabs(self.build_dir)

        shutil.make_archive(
            base_name=Path(self.root_dir, self.mod_name),
            format="zip",
            root_dir=self.build_dir,
        )

        if clean:
            shutil.rmtree(self.build_dir)

    def _install(self, path: Path):
        """
        TODOC
        """
        if path.exists():
            shutil.rmtree(path)

        with ZipFile(self.zip_archive, "r") as zip_file:
            zip_file.extractall(path)

    def install_local(self):
        """
        TODOC
        """
        self._install(self.mod_path)

    def install_server(self):
        """
        TODOC
        """
        if config.PATH_7D2D_SERVER is None:
            raise ValueError("PATH_7D2D_SERVER is not defined.")

        path = Path(config.PATH_7D2D_SERVER, "../Mods", self.mod_name)
        self._install(path)

    def start_local(self):

        subprocess.Popen(
            cwd=self.game_path,
            executable=Path(self.game_path, "7DaysToDie.exe"),
            args=["--noeac"],
        )

        self._clear_saves()

    def start_server(self):
        """
        TODOC
        """
        if config.PATH_7D2D_SERVER is None:
            raise ValueError("PATH_7D2D_SERVER is not defined.")

        server_directory = config.PATH_7D2D_SERVER.parent

        subprocess.Popen(
            cwd=server_directory,
            executable=Path(server_directory, "startdedicated.bat"),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            args=[],
        )

    def shut_down(self):
        """
        TODOC
        """
        subprocess.run("taskkill /F /IM 7DaysToDie.exe", capture_output=True)
        subprocess.run("taskkill /F /IM 7DaysToDieServer.exe", capture_output=True)

    def fetch_prefabs(self, root: Path = None):

        if not self.prefabs:
            return

        if root is None:
            root = self.root_dir

        dst_prefabs = Path(root, "Prefabs").resolve()

        if dst_prefabs.exists():
            shutil.rmtree(dst_prefabs)

        for element in self.prefabs:

            prefabs = glob.glob(f"{element}*", root_dir=config.PATH_PREFABS)

            if not prefabs:
                print(f"WRN: no prefab found for '{element}'")

            for path in prefabs:

                src = Path(config.PATH_PREFABS, path)
                dst = Path(dst_prefabs, src.name)

                if not dst.parent.exists():
                    os.makedirs(dst.parent)

                if src.is_file():
                    shutil.copyfile(src, dst)

                else:
                    shutil.copytree(src, dst, dirs_exist_ok=True)

    def release(self) -> Path:
        """
        TODOC
        """
        start = time.time()
        self.build()

        shutil.rmtree(self.build_dir, ignore_errors=True)
        os.makedirs(self.build_dir)

        dependencies = self._build_dependencies()

        for builder in dependencies + [self]:

            dst = Path(self.build_dir, builder.zip_archive.stem)

            with ZipFile(builder.zip_archive, "r") as zip_file:
                zip_file.extractall(dst)

        with open(Path(self.build_dir, self.mod_name, "version.txt"), "w") as writer:

            combined_hash = self._combine_commit_hashes(dependencies)

            writer.write(f"version={combined_hash}\n")
            writer.write(f"{self.mod_name}={self.commit_hash.__str__()}\n")

            for dep in dependencies:
                writer.write(f"{dep.mod_name}={dep.commit_hash.__str__()}\n")

        shutil.make_archive(f"{self.mod_name}-release-{combined_hash[:8]}", "zip", self.build_dir)

        print(f"build {combined_hash[:8]} done in {time.time() - start:.1f}s")

        return self.zip_archive

    def show_infos(self) -> None:
        """
        TODOC
        """
        print(f"mod_name ..... : {self.mod_name}")
        print(f"commit_hash .. : {self.commit_hash}")
        print()
        print(f"root_dir ..... : {self.root_dir}")
        print(f"build_dir .... : {self.build_dir}")
        print(f"csproj ....... : {self.csproj}")
        print(f"zip_archive .. : {self.zip_archive}")
        print()
        print(f"game_path .... : {self.game_path}")
        print(f"mod_path ..... : {self.mod_path}")
        print()


# fmt: off
@click.command("build")
@click.option("-c", "--clean", is_flag=True, help="Clean the build directory, once done.")
@click.option("-q", "--quiet", is_flag=True, help="Hide dotnet outputs.")
def cmd_build(clean: bool, quiet: bool):
    """
    Compile the project in the current working directory and create a zip archive ready for testing
    """
    ModBuilder().build(clean, quiet)


@click.command("start")
@click.option("-s", "--server", is_flag=True)
def cmd_start_local(server: bool):
    """
    Compile the project, then start a local game
    """
    builder = ModBuilder()
    builder.shut_down()
    builder.build()
    builder.install_local()
    builder.start_local()

    if server:
        builder.install_server()
        builder.start_server()


@click.command("shut-down")
def cmd_shut_down():
    """
    Hard closes all instances of 7DaysToDie.exe and 7DaysToDieServer.exe
    """
    ModBuilder().shut_down()


@click.command("release")
def cmd_release():
    """
    Compile the project and create the release zip archive
    """
    ModBuilder().release()


@click.command("fetch-prefabs")
def cmd_fetch_prefabs():
    """
    Copy all prefabs specified in `build.json/prefabs` into the folder `Prefab` of the current working directory
    """
    ModBuilder().fetch_prefabs()


@click.command("install")
def cmd_install():
    """
    Build the project then install the mod in the 7 days Mods folder
    """
    builder = ModBuilder()
    builder.shut_down()
    builder.build()
    builder.install_local()


@click.command("infos")
def cmd_infos():
    """
    Show dumped infos of the current build.json file
    """
    ModBuilder().show_infos()