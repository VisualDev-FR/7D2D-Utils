import os
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom
from xml.etree.ElementTree import Element
from pathlib import Path

import click

SD_DIR = os.environ["PATH_7D2D"]

SD_CONFIG_DIR = Path(SD_DIR, "Data/Config")


def prettify_xml(element: Element) -> str:
    """
    TODOC
    """
    str_element = ET.tostring(element, encoding="utf-8", method="xml")

    pretty_element = minidom.parseString(str_element).toprettyxml(newl="")

    return pretty_element[22:]


def send_xpath(file: str, request: str) -> Element:
    """
    TODOC
    """
    absolute_path = Path(SD_CONFIG_DIR, file)

    if not absolute_path.exists():
        click.echo(f"Invalid file: {file}")
        return

    root_element = ET.parse(absolute_path).getroot()

    target_element = root_element.find(request)

    return target_element


@click.command
@click.argument("file", required=True)
@click.argument("request", required=True)
def xpath(file: str, request: str) -> Element:
    """
    Send an xpath request to a given xml file

    FILE:    The relative path to the target file, from the folder 7DaysToDie/Data/Config
    REQUEST: The xpath request to send
    """
    absolute_path = Path(SD_CONFIG_DIR, file)

    if not absolute_path.exists():
        click.echo(f"Invalid file: {file}")
        return

    root_element = ET.parse(absolute_path).getroot()

    target_element = root_element.find(request)

    click.echo(prettify_xml(target_element))


@click.command
@click.argument(
    "block_name",
    type=str,
    required=True,
)
def block(block_name: str):
    """
    Diplay block datas from a given block name.

    BLOCK_NAME: the name of the block you want to display
    """
    blocks_path = Path(SD_CONFIG_DIR, "blocks.xml")

    blocks_root = ET.parse(blocks_path).getroot()

    target_block = blocks_root.find(f"./block[@name='{block_name}']")

    click.echo(prettify_xml(target_block))


@click.command
@click.argument("file", required=True)
@click.option("-e", "--editor", default='""', help="The editor which with you want to open the file (must be added to your path env variable)")
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
