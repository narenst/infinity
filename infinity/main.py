import click

from infinity.command.list import list
from infinity.command.start import start
from infinity.command.stop import stop
from infinity.command.create import create
from infinity.command.update import update

# import ptvsd
# print("Waiting for debugger attach")
# ptvsd.enable_attach(address=('localhost', 5678), redirect_output=True)
# ptvsd.wait_for_attach()


@click.group()
def cli():
    pass


# Mount the individual commands here
cli.add_command(list)
cli.add_command(start)
cli.add_command(stop)
cli.add_command(create)
cli.add_command(update)