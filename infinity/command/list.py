import click
from tabulate import tabulate

from infinity.aws.auth import get_session
from infinity.aws.instance import get_infinity_volumes


@click.command()
def list():
    """
    List all the infinity machines
    """
    session = get_session()
    ec2_resource = session.resource('ec2')

    volumes = get_infinity_volumes(session=session)
    info = []

    for volume in volumes:
        specs = [volume.id, volume.size, volume.state]
        if volume.attachments: 
            ec2_instance_id = volume.attachments[0]['InstanceId']
            ec2_instance = ec2_resource.Instance(id=ec2_instance_id)
            specs = specs + [ec2_instance.id, ec2_instance.state['Name'], ec2_instance.instance_type]
        else:
            specs = specs + ['-', 'waiting for snapshot', '-']
        info.append(specs)

    headers = ["ID", "DISK SIZE", "DISK STATE", "MACHINE ID", "MACHINE STATE", "MACHINE TYPE"]
    print(tabulate(info, headers=headers))