from pathlib import Path
import shutil
import os
import subprocess

import _click as click


MOD_NAME_PROP = "@MODNAME"


def _render_template(filename: Path, datas: dict):
    """
    TODOC
    """
    with open(filename, "r") as reader:
        content = reader.read()

    for key, value in datas.items():
        content = content.replace(key, value)

    with open(filename, "w") as writer:
        writer.write(content)


@click.command("new")
@click.argument("mod-name")
def cmd_new(mod_name: str):
    """
    Creates a new 7D2D Modding project
    """

    PLACEHOLDERS = {MOD_NAME_PROP: mod_name}

    starter_dir = Path(__file__, "../../_starter").resolve()

    if Path(mod_name).exists():
        raise SystemExit(f"Error: A folder with name '{mod_name}' already exists")

    # fmt: off
    os.makedirs(mod_name)
    os.makedirs(Path(mod_name, "Config"))
    os.makedirs(Path(mod_name, "Resources"))
    os.makedirs(Path(mod_name, "Scripts"))
    os.makedirs(Path(mod_name, "Harmony"))
    os.makedirs(Path(mod_name, "Prefabs"))
    os.makedirs(Path(mod_name, "UIAtlases/ItemIconAtlas"))

    shutil.copy(Path(starter_dir, "ModInfo.xml"), Path(mod_name, "ModInfo.xml"))
    shutil.copy(Path(starter_dir, ".csproj"), Path(mod_name, f"{mod_name}.csproj"))
    shutil.copy(Path(starter_dir, "gitignore.template"), Path(mod_name, ".gitignore"))
    shutil.copy(Path(starter_dir, "ModApi.cs"), Path(mod_name, "Harmony/ModApi.cs"))
    shutil.copy(Path(starter_dir, "build.json"), Path(mod_name, "build.json"))
    # fmt: on

    _render_template(Path(mod_name, f"{mod_name}.csproj"), PLACEHOLDERS)
    _render_template(Path(mod_name, "ModInfo.xml"), PLACEHOLDERS)
    _render_template(Path(mod_name, "Harmony/ModApi.cs"), PLACEHOLDERS)
    _render_template(Path(mod_name, "build.json"), PLACEHOLDERS)

    subprocess.run(f"git init {Path(mod_name)}", capture_output=True)
