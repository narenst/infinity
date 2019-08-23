import click
import os

from infinity.aws.auth import get_session
from infinity.command.volume import volume
from infinity.command.volume.list import print_volume_info
from infinity.settings import get_infinity_settings


@volume.command()
@click.argument('volume-id')
@click.option('--instance-id', required=True, type=str, help="ID of instance to attach to")
def attach(volume_id, instance_id):
    """
    Attach the volume to the instance
    """
    ec2_resource = get_session().resource('ec2')

    # Check if volume is already attached to a device
    volume = ec2_resource.Volume(volume_id)
    if volume.attachments:
        raise Exception("Volume is currently already attached to an instance")

    instance = ec2_resource.Instance(instance_id)

    # Check if instance already has another secondary disk
    for attachment in instance.block_device_mappings:
        if attachment['DeviceName'] == '/dev/sdh':
            raise Exception(f"Instance {instance_id} already has a secondary volume attached to it")

    # Check if instance is stopped
    if not instance.state['Name'] in ['stopped', 'running']:
        raise Exception(f"Volume can be mounted only to a stopped or running instance. Current state: {instance.state['Name']}")

    print("Attaching volume to the instance...")

    volume.attach_to_instance(
        Device='/dev/sdh',
        InstanceId=instance_id,
    )

    ec2_client = get_session().client('ec2')
    waiter = ec2_client.get_waiter('volume_in_use')
    waiter.wait(VolumeIds=[volume_id])

    print("Volume successfully attached to instance")

    if instance.state['Name'] == 'running':
        print("Mounting the disk to the running machine at: /data")
        # Connect to the machine and run /etc/load_volume.sh script
        ssh_private_key_path = get_infinity_settings().get('ssh_private_key_path')

        # Ignore the KeyChecking since the hosts are trusted
        ssh_command = f"ssh -oStrictHostKeyChecking=no -i {ssh_private_key_path} ubuntu@{instance.public_ip_address} sudo /etc/load_volume.sh"

        os.environ["PYTHONUNBUFFERED"] = "1"
        os.system(ssh_command)

    response = ec2_client.describe_volumes(
        VolumeIds=[
            volume_id
        ]
    )
    print_volume_info(response['Volumes'])