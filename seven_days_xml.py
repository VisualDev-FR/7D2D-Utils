import os
import xml.dom.minidom as minidom
from xml.etree.ElementTree import Element
from pathlib import Path
import lxml.etree as ET

import click

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
@click.option("--no-comments", is_flag=True, help="Enable this option to ignore comments.")
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

        prettified = [prettify_xml(element, not no_comments) for element in target_element]

        click.echo("\n".join(prettified))
        click.echo(f"{len(target_element)} results.")

    except Exception as e:
        click.echo(f"Bad request: {e.__repr__()}")


@click.command
@click.option(
    "--name",
    type=str,
    required=False,
    help="Filter blocks by name"
)
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
def open(file: str, editor: str):
    """
    Open a given xml file with the default program defined from xml files.

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

    absolute_path = Path(SD_CONFIG_DIR, "blocks.xml")

    target_element = ET.parse(absolute_path).findall("./block[@name='terrDirt']")

    prettified = [prettify_xml(element) for element in target_element]

    click.echo("\n".join(prettified))