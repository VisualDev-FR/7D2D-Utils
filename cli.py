import _click as click

from commands.new import cmd_new
from commands.build import (
    cmd_compile,
    cmd_release,
    cmd_shut_down,
    cmd_start_local,
    cmd_start_server,
)


@click.group()
def cli():
    """
    A set of commands to manage 7 days to die modding projects.
    """
    pass


# new.py
cli.add_command(cmd_new)

# build.py
cli.add_command(cmd_compile)
cli.add_command(cmd_release)
cli.add_command(cmd_start_server)
cli.add_command(cmd_start_local)
cli.add_command(cmd_shut_down)


if __name__ == "__main__":
    cli()
