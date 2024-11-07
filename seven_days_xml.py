import shutil
import os
import xml.dom.minidom as minidom
from xml.etree.ElementTree import Element
from pathlib import Path
import json
from pprint import pprint

import click
import lxml.etree as ET


SD_DIR = os.environ["PATH_7D2D"]

SD_CONFIG_DIR = Path(SD_DIR, "Data/Config")


def prettify_xml(element: Element, with_comments: bool = True) -> str:
    """
    TODOC
    """

    # c14n method is mandatory to allow ignoring comments
    str_element = ET.tostring(element, method="c14n", with_comments=with_comments)

    pretty_element = minidom.parseString(str_element).toprettyxml(newl="", indent="")

    return pretty_element[22:]


@click.command
@click.argument("file", required=True)
@click.argument("request", required=True)
@click.option(
    "--no-comments", is_flag=True, help="Enable this option to ignore comments."
)
def xpath(file: str, request: str, no_comments: bool) -> Element:
    """
    Send an xpath request to a given xml file

    FILE:    The relative path to the target file, from the folder 7DaysToDie/Data/Config
    REQUEST: The xpath request to send
    """
    absolute_path = Path(SD_CONFIG_DIR, file)

    if not absolute_path.exists():
        click.echo(f"Invalid file: {file}")
        return

    try:
        target_element = ET.parse(absolute_path).xpath(request)

        prettified = [
            prettify_xml(element, not no_comments) for element in target_element
        ]

        click.echo("\n".join(prettified))
        click.echo(f"{len(target_element)} results.")

    except Exception as e:
        click.echo(f"Bad request: {e.__repr__()}")


@click.command
@click.option("--name", type=str, required=False, help="Filter blocks by name")
@click.option(
    "--ls",
    is_flag=True,
    help="Enable this option to display all available blocks.",
)
def block(name: str, ls: bool):
    """
    Diplay block datas from a given block name.
    """
    blocks_path = Path(SD_CONFIG_DIR, "blocks.xml")

    blocks_tree = ET.parse(blocks_path)

    if ls:
        all_blocks = blocks_tree.findall(".//block")
        for block in all_blocks:
            click.echo(block.attrib["name"])
        click.echo(f"{len(all_blocks)} Results.")
        return

    if name is not None:
        target_block = blocks_tree.find(f"./block[@name='{name}']")

    else:
        raise click.exceptions.BadParameter("name or xpath option must be specified.")

    if target_block is None:
        click.echo(f"Not result for '{name}'")
        return

    click.echo(prettify_xml(target_block))


@click.command
@click.argument("file", required=True)
@click.option(
    "-e",
    "--editor",
    default='""',
    help="The editor which with you want to open the file (must be added to your path env variable)",
)
def reveal(file: str, editor: str):
    """
    Open a given xml file with the default program.

    FILE:    The relative path to the target file, from the folder 7DaysToDie/Data/Config
    """
    absolute_path = Path(SD_CONFIG_DIR, file)

    if not absolute_path.exists():
        click.echo(f"Invalid file: {file}")
        return

    os.system(f'start {editor} "{absolute_path}"')


@click.command
def ls_xml():
    """
    Display the list of all available xml files
    """

    xml_files = []

    for root, dirs, files in os.walk(SD_CONFIG_DIR):
        for file in files:
            xml_files.append(Path(root, file).relative_to(SD_CONFIG_DIR).__str__())

    click.echo("\n".join(xml_files))


@click.command
@click.argument("keyword")
@click.option("--search", is_flag=True)
def getlocal(keyword: str, search: bool):
    """
    Display translations for a given keyword from Localization.txt
    """
    localization_path = Path(SD_CONFIG_DIR, "Localization.txt")

    with open(localization_path, "rb") as reader:
        file_content = reader.readlines()

    headers = file_content[0].decode("utf-8")[:-2].split(",")

    translations = dict()
    matching_keywords = set() if search else set(keyword)

    for datas in file_content[1:]:

        splitted = datas.decode("utf-8")[:-2].split(",")
        key = splitted[0]
        translations[key] = splitted

        if search and keyword.lower() in key.lower():
            matching_keywords.add(key)

    for kw in matching_keywords:

        if kw not in translations:
            continue

        datas = translations[kw]

        for lang, value in zip(headers, datas):
            click.echo(f"{lang:.<15} {value}")

        click.echo()

    if search:
        print(f"{len(matching_keywords)} results.")


@click.command
@click.argument("mod-name")
def new(mod_name: str):
    """
    Creates a new 7D2D Modding project
    """
    MOD_NAME_PROP = "@MODNAME"
    DATAS = {MOD_NAME_PROP: mod_name}

    starter_dir = Path(Path(__file__).parent, "starter")

    if Path(mod_name).exists():
        click.echo(f"Error: A folder with name '{mod_name}' already exists")
        return

    # fmt: off
    os.makedirs(mod_name)
    os.makedirs(Path(mod_name, "Config"))
    os.makedirs(Path(mod_name, "Resources"))
    os.makedirs(Path(mod_name, "Scripts"))
    os.makedirs(Path(mod_name, "Harmony"))
    os.makedirs(Path(mod_name, "UIAtlases/ItemIconAtlas"))

    shutil.copytree(Path(starter_dir, "Helpers"), Path(mod_name, "Helpers"))
    shutil.copy(Path(starter_dir, "ModInfo.xml"), Path(mod_name, "ModInfo.xml"))
    shutil.copy(Path(starter_dir, ".csproj"), Path(mod_name, f"{mod_name}.csproj"))
    shutil.copy(Path(starter_dir, "gitignore.template"), Path(mod_name, ".gitignore"))
    shutil.copy(Path(starter_dir, "ModApi.cs"), Path(mod_name, "Harmony/ModApi.cs"))
    # fmt: on

    def render_template(filename: Path, datas: dict):

        with open(filename, "r") as reader:
            content = reader.read()

        for key, value in datas.items():
            content = content.replace(key, value)

        with open(filename, "w") as writer:
            writer.write(content)

    render_template(Path(mod_name, f"{mod_name}.csproj"), DATAS)
    render_template(Path(mod_name, "ModInfo.xml"), DATAS)
    render_template(Path(mod_name, "Harmony/ModApi.cs"), DATAS)
    render_template(Path(mod_name, "Helpers/compile.cmd"), DATAS)

    os.system(f"git init {Path(mod_name)}")
