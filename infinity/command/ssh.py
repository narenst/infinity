import click
import os

from infinity.aws.auth import get_session
from infinity.settings import get_infinity_settings


@click.command()
@click.argument('id')
@click.option('--print-command-only/--no-print-command-only', default=False)
def ssh(id, print_command_only):
    """
    SSH into the infinity machine.

    This command uses the private key configured in the settings file (~/.infinity/settings.yaml)
    to connect.
    """
    ec2_resource = get_session().resource('ec2')
    instance = ec2_resource.Instance(id)

    ssh_private_key_path = get_infinity_settings().get('ssh_private_key_path')

    # Ignore the KeyChecking since the hosts are trusted
    ssh_command = f"ssh -oStrictHostKeyChecking=no -i {ssh_private_key_path} ubuntu@{instance.public_ip_address}"

    if print_command_only:
        print(ssh_command)
    else:
        os.environ["PYTHONUNBUFFERED"] = "1"
        os.system(ssh_command)