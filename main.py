import click

from seven_days_xml import (
    block,
    xpath,
    reveal,
    ls_xml,
    getlocal,
)

@click.group()
def Seven_days_utils():
    """
    A bunch of commands to access the 7Days to die files.
    """
    pass


Seven_days_utils.add_command(block)
Seven_days_utils.add_command(xpath)
Seven_days_utils.add_command(reveal)
Seven_days_utils.add_command(ls_xml)
Seven_days_utils.add_command(getlocal)


if __name__ == "__main__":
    Seven_days_utils()