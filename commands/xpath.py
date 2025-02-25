import shutil
import os
import xml.dom.minidom as minidom
from xml.etree.ElementTree import Element
from pathlib import Path

import _click
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


@_click.command
@_click.argument("file", required=True)
@_click.argument("request", required=True)
@_click.option(
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
        print(f"Invalid file: {file}")
        return

    try:
        target_element = ET.parse(absolute_path).xpath(request)

        prettified = [
            prettify_xml(element, not no_comments) for element in target_element
        ]

        print("\n".join(prettified))
        print(f"{len(target_element)} results.")

    except Exception as e:
        print(f"Bad request: {e.__repr__()}")


@_click.command
@_click.option("--name", type=str, required=False, help="Filter blocks by name")
@_click.option(
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
            print(block.attrib["name"])
        print(f"{len(all_blocks)} Results.")
        return

    if name is not None:
        target_block = blocks_tree.find(f"./block[@name='{name}']")

    else:
        raise _click.exceptions.BadParameter("name or xpath option must be specified.")

    if target_block is None:
        print(f"Not result for '{name}'")
        return

    print(prettify_xml(target_block))


@_click.command
@_click.argument("file", required=True)
@_click.option(
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
        print(f"Invalid file: {file}")
        return

    os.system(f'start {editor} "{absolute_path}"')


@_click.command
def ls_xml():
    """
    Display the list of all available xml files
    """

    xml_files = []

    for root, dirs, files in os.walk(SD_CONFIG_DIR):
        for file in files:
            xml_files.append(Path(root, file).relative_to(SD_CONFIG_DIR).__str__())

    print("\n".join(xml_files))


@_click.command
@_click.argument("keyword")
@_click.option("--search", is_flag=True)
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
            print(f"{lang:.<15} {value}")

        print()

    if search:
        print(f"{len(matching_keywords)} results.")
