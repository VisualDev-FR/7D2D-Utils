import click

from seven_days_xml import (
    block,
    xpath,
    open as open_7D,
    ls_xml,
)

@click.group()
def Seven_days_utils():
    """
    A bunch of commands to access the 7Days to die files.
    """
    pass


Seven_days_utils.add_command(block)
Seven_days_utils.add_command(xpath)
Seven_days_utils.add_command(open_7D)
Seven_days_utils.add_command(ls_xml)


if __name__ == "__main__":
    Seven_days_utils()