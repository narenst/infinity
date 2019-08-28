import click
import os

from infinity.aws.auth import get_session
from infinity.settings import get_infinity_settings


@click.command()
@click.argument('id')
@click.option('--print-command-only/--no-print-command-only', default=False)
@click.option('--local-port', type=int, default=8888)
@click.option('--infinity-machine-port', type=int, default=8888)
def jupyter(id, print_command_only, local_port, infinity_machine_port):
    """
    Setup port forwarding for Jupyter Lab.

    This will SSH into the instance and forward the infinity-machine-port to the local machine.
    Gives a secure option to connect to your Jupyter Lab instance. Note: You need to run Jupyter Lab
    for this command to work.
    """
    ec2_resource = get_session().resource('ec2')
    instance = ec2_resource.Instance(id)

    ssh_private_key_path = get_infinity_settings().get('ssh_private_key_path')

    # Ignore the KeyChecking since the hosts are trusted
    ssh_command = f"ssh -N -f -oStrictHostKeyChecking=no -oExitOnForwardFailure=yes -i {ssh_private_key_path} " \
        f"ubuntu@{instance.public_ip_address} -L localhost:{local_port}:localhost:{infinity_machine_port}"

    if print_command_only:
        print(ssh_command)
    else:
        code = os.system(ssh_command)
        if code == 0:
            print(f"Port forwarding setup from {instance.public_ip_address}:{infinity_machine_port} -> "
                  f"localhost:{local_port}")
            print(f"After running Jupyter on the infinity machine, open http://localhost:{local_port}")