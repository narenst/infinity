import click
from tabulate import tabulate

from infinity.aws.auth import get_session
from infinity.aws.instance import get_infinity_instances


def get_name_from_tags(tags):
    """
    In the AWS tags list identify the Name tag and return that
    """
    for tag in tags:
        if tag["Key"] == "Name":
            return tag["Value"]
    else:
        return None


@click.command()
def list():
    """
    List all the infinity machines
    """
    session = get_session()
    ec2_resource = session.resource('ec2')
    instances = get_infinity_instances(session=session)

    machine_info = []
    for instance in instances:
        root_volume_id = instance.block_device_mappings[0]['Ebs']['VolumeId']
        root_volume = ec2_resource.Volume(id=root_volume_id)
        machine_info.append([instance.id,
                             get_name_from_tags(instance.tags),
                             instance.instance_type,
                             root_volume.size,
                             instance.state['Name']])

    headers = ["ID", "NAME", "MACHINE TYPE", "DISK", "STATUS"]
    print(tabulate(machine_info, headers=headers))