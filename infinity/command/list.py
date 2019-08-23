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


def print_machine_info(instances):
    """
    Print a table with the machine info
    """
    ec2_resource = get_session().resource('ec2')
    machine_info = []
    for instance in instances:
        if instance.block_device_mappings:
            root_volume_id = instance.block_device_mappings[0]['Ebs']['VolumeId']
            root_volume = ec2_resource.Volume(id=root_volume_id)
            root_volume_size = root_volume.size
        else:
            root_volume_size = '-'

        machine_info.append([instance.id,
                             get_name_from_tags(instance.tags),
                             instance.instance_type,
                             instance.instance_lifecycle or 'on-demand',
                             instance.public_ip_address,
                             root_volume_size,
                             instance.state['Name']])

    headers = ["ID", "NAME", "MACHINE TYPE", "TYPE", "IP", "DISK", "STATUS"]
    print(tabulate(machine_info, headers=headers))


@click.command()
def list():
    """
    List all the infinity machines
    """
    instances = get_infinity_instances(session=get_session())
    print_machine_info(instances)