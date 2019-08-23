import click
import random
import string

from infinity.aws.auth import get_session
from infinity.command.volume import volume
from infinity.command.volume.list import print_volume_info


@volume.command()
@click.option('--reference-instance-id', 'instance_id', type=str, help="ID of reference instance for the volume")
@click.option('--az', 'volume_az', type=str, help="Availability zone")
@click.option('--size', default=100, type=int, help='Disk size in GBs')
def create(instance_id, volume_az, size):
    ec2_resource = get_session().resource('ec2')

    if instance_id:
        instance = ec2_resource.Instance(instance_id)
        az = instance.placement['AvailabilityZone']
    elif volume_az:
        az = volume_az
    else:
        raise Exception("Specify one of --az or --reference-instance-id")

    # # Ensure the instance does not already have a secondary disk
    # for block_device in instance.block_device_mappings:
    #     if block_device['DeviceName'] == '/dev/sdh':
    #         raise Exception(f"Instance already has a secondary volume attached to it: {block_device['Ebs']['VolumeId']}")

    ec2_client = get_session().client('ec2')
    machine_name_suffix = ''.join(random.choice(string.ascii_lowercase) for x in range(10))

    response = ec2_client.create_volume(
        AvailabilityZone=az,
        VolumeType='gp2',
        Size=size,
        TagSpecifications=[
            {
                "ResourceType": "volume",
                "Tags": [
                    {
                        "Key": "Name",
                        "Value": f"infinity-{machine_name_suffix}"
                    },
                    {
                        "Key": "type",
                        "Value": "infinity"
                    }
                ]
            }
        ]
    )

    volume_id = response['VolumeId']
    print(f"Created new volume with id: {volume_id}")

    waiter = ec2_client.get_waiter('volume_available')
    waiter.wait(VolumeIds=[volume_id])

    # response = ec2_client.attach_volume(
    #     Device='/dev/sdh',
    #     InstanceId=instance_id,
    #     VolumeId=volume_id,
    # )

    # waiter = ec2_client.get_waiter('volume_in_use')
    # waiter.wait(VolumeIds=[volume_id])

    # print(f"Successfully attached the new volume {volume_id} to instance {instance_id}")
    response = ec2_client.describe_volumes(
        VolumeIds=[
            volume_id
        ]
    )
    print_volume_info(response['Volumes'])