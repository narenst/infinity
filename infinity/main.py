import click

from infinity.command.list import list
from infinity.command.start import start
from infinity.command.stop import stop
from infinity.command.create import create
from infinity.command.update import update
from infinity.command.destroy import destroy
from infinity.command.setup import setup
from infinity.command.teardown import teardown
from infinity.command.ssh import ssh
from infinity.command.jupyter import jupyter
from infinity.command.quota import quota
from infinity.command.price import price

from infinity.command.volume import volume
from infinity.command.volume.list import list as volume_list # noqa
from infinity.command.volume.create import create as volume_create # noqa
from infinity.command.volume.detach import detach as volume_detach # noqa
from infinity.command.volume.attach import attach as volume_attach # noqa
from infinity.command.volume.destroy import destroy as volume_destroy # noqa
from infinity.command.volume.update import update as volume_update # noqa


@click.group()
def cli():
    pass


# Mount the individual commands here
cli.add_command(list)
cli.add_command(start)
cli.add_command(stop)
cli.add_command(create)
cli.add_command(update)
cli.add_command(destroy)
cli.add_command(setup)
cli.add_command(teardown)
cli.add_command(ssh)
cli.add_command(jupyter)
cli.add_command(quota)
cli.add_command(price)
cli.add_command(volume)