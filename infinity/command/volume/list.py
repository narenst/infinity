from tabulate import tabulate

from infinity.aws.auth import get_session
from infinity.command.volume import volume
from infinity.command.list import get_name_from_tags


def print_volume_info(volumes):
    volume_info = []
    for vol in volumes:
        attachments = vol['Attachments']
        if attachments:
            instance_id = attachments[0]['InstanceId']
            if attachments[0]['Device'] == '/dev/sda1':
                disk_type = 'root'
            else:
                disk_type = 'secondary'
        else:
            instance_id = 'N/A'
            disk_type = 'N/A'

        volume_info.append(
            [
                vol['VolumeId'],
                get_name_from_tags(vol['Tags']),
                vol['Size'],
                vol['State'],
                vol['AvailabilityZone'],
                instance_id,
                disk_type
            ]
        )

    headers = ["VOLUME ID", "NAME", "DISK SIZE", "STATUS", "AVAILABILITY ZONE", "ATTACHED INSTANCE ID", "DISK TYPE"]
    print(tabulate(volume_info, headers=headers))


@volume.command()
def list():
    """
    Prints a list of all your volumes.

    Useful to see all the volumes in one place. The volumes must have an AWS tag
    type=infinity for the volume to show up in this list.
    """
    ec2_client = get_session().client('ec2')
    response = ec2_client.describe_volumes(
        Filters=[
            {
                'Name': 'tag:type',
                'Values': ['infinity']
            }
        ]
    )
    print_volume_info(response['Volumes'])