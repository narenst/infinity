import click

from infinity.aws.auth import get_session
from infinity.command.volume import volume


@volume.command()
@click.argument('volume-id')
@click.option('--size', type=int, help="Increase the disk size (in GBs)")
@click.option('--name', help='Set the name of the machine')
def update(volume_id, size, name):
    """
    Update volume specs
    """
    ec2_resource = get_session().resource('ec2')
    ec2_client = get_session().client('ec2')
    volume = ec2_resource.Volume(volume_id)

    if name:
        print(f"Updating volume name to: {name}...")
        volume.create_tags(
            Tags=[
                {
                    "Key": "Name",
                    "Value": name,
                }
            ]
        )

    if size:
        print(f"Updating disk size to: {size}...")
        response = ec2_client.modify_volume(
            VolumeId=volume_id,
            Size=size
        )
        status = response['VolumeModification']['ModificationState']
        print(f"Disk is currently in {status} state. It may take a few minutes for the size change to finish")