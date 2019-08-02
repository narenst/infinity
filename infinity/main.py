import click

from infinity.command.list import list
from infinity.command.start import start
from infinity.command.stop import stop


@click.group()
def cli():
    pass


# Mount the individual commands here
cli.add_command(list)
cli.add_command(start)
cli.add_command(stop)