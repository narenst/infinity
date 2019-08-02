import click
from tabulate import tabulate

from infinity.aws.auth import get_session
from infinity.aws.instance import get_infinity_instances


@click.command()
def list():
    """
    List all the infinity machines
    """
    session = get_session()
    instances = get_infinity_instances(session=session)

    machine_info = []
    for instance in instances:
        machine_info.append([instance.id,
                             instance.tags[0]['Value'],
                             instance.instance_type,
                             instance.state['Name'],
                            #  instance.cpu_options['CoreCount'],
                            #  instance.image_id,
                             instance.spot_instance_request_id])

    headers = ["ID", "NAME", "MACHINE TYPE", "STATUS", "SPOT REQ ID"]
    print(tabulate(machine_info, headers=headers))