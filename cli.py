import _click as click

from commands.new import cmd_new
from commands.update import cmd_update
from commands.bbcode import cmd_bbcode_to_html
from commands.build import (
    cmd_build,
    cmd_release,
    cmd_install,
    cmd_shut_down,
    cmd_start_local,
    cmd_start_server,
    cmd_fetch_prefabs,
)

ascii = r"""
  ______ _____      _    _ _______ _____ _       _____
 |____  |  __ \    | |  | |__   __|_   _| |     / ____|
     / /| |  | |___| |  | |  | |    | | | |    | (___
    / / | |  | |___| |  | |  | |    | | | |     \___ \
   / /  | |__| |   | |__| |  | |   _| |_| |____ ____) |
  /_/   |_____/     \____/   |_|  |_____|______|_____/
"""


class CustomHelp(click.Group):
    def get_help(self, ctx):
        return f"{ascii}\n{super().get_help(ctx)}"


@click.group(cls=CustomHelp, context_settings={"max_content_width": 120})
def cli():
    """
    A set of commands to manage 7 days to die modding projects.
    """
    pass


# new.py
cli.add_command(cmd_new)

# update.py
cli.add_command(cmd_update)

# build.py
cli.add_command(cmd_build)
cli.add_command(cmd_release)
cli.add_command(cmd_fetch_prefabs)
cli.add_command(cmd_start_server)
cli.add_command(cmd_start_local)
cli.add_command(cmd_shut_down)
cli.add_command(cmd_install)

# bbcode.py
cli.add_command(cmd_bbcode_to_html)


if __name__ == "__main__":
    cli()
