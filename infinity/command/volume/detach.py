import click

from infinity.aws.auth import get_session
from infinity.command.volume import volume
from infinity.command.volume.list import print_volume_info


@volume.command()
@click.argument('volume-id')
def detach(volume_id):
    """
    Detach the volume from its instance.

    The detached volume can then be attached to any other instance.
    """
    ec2_resource = get_session().resource('ec2')
    volume = ec2_resource.Volume(volume_id)
    if not volume.attachments:
        raise Exception("Volume is currently not attached to any instance")

    instance_id = volume.attachments[0]['InstanceId']
    instance = ec2_resource.Instance(instance_id)

    if not instance.state['Name'] == 'stopped':
        raise Exception("Cannot unmount disk from a running instance")

    print("Detaching volume from instance...")

    volume.detach_from_instance(
        InstanceId=instance_id,
    )

    ec2_client = get_session().client('ec2')
    waiter = ec2_client.get_waiter('volume_available')
    waiter.wait(VolumeIds=[volume_id])

    print("Volume successfully detached from instance")

    response = ec2_client.describe_volumes(
        VolumeIds=[
            volume_id
        ]
    )
    print_volume_info(response['Volumes'])