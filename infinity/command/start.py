import click

from infinity.aws.auth import get_session
from infinity.aws.instance import get_specific_instance, get_snapshots_by_volume_id


@click.command()
@click.argument('id', nargs=1)
def start(id):
    """
    Start the cloud machine with the id
    """
    session = get_session()
    ec2_resource = session.resource('ec2')

    volume = ec2_resource.Volume(id=id)

    if volume.state == 'in-use':
        ec2_instance_id = volume.attachments[0]['InstanceId']
        ec2_instance = ec2_resource.Instance(id=ec2_instance_id)
        raise Exception(f"Active instance with this volume: {ec2_instance.state}")

    if volume.state != 'available':
        raise Exception(f"Disk is in a bad state: {volume.state}")

    # Check if latest snapshot exists for this volume
    snapshots = get_snapshots_by_volume_id(session, volume.id)

    if not snapshots:
        print("Creating a snapshot first")