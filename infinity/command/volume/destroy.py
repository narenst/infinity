import click

from infinity.aws.auth import get_session
from infinity.command.volume import volume


@volume.command()
@click.argument('volume-id')
def destroy(volume_id):
    """
    Destroy the volume.

    Can only be run when it is not attached to any instance. The disk is
    not recoverable after destroying.
    """
    ec2_resource = get_session().resource('ec2')
    volume = ec2_resource.Volume(volume_id)
    if volume.attachments:
        raise Exception(f"Volume is currently not attached to instance: {volume.attachments[0]['InstanceId']}")

    if click.confirm("\nAre you sure you want to destroy the volume? This is irrrecoverable."):

        print("Destroying volume ...")
        volume.delete()

        print("Destroy successful, it may take a few seconds to fully destroy the volume ...")
        ec2_client = get_session().client('ec2')
        waiter = ec2_client.get_waiter('volume_deleted')
        waiter.wait(VolumeIds=[volume_id])

        print("Destroy complete")