import click

from infinity.aws.auth import get_session
from infinity.command.list import print_machine_info


@click.command()
@click.argument('id')
@click.option('--size', type=int, help="Increase the disk size (in GBs)")
@click.option('--type', 'instance_type', help="Switch the AWS instance type. Ex: p2.xlarge, t3.large")
@click.option('--name', help='Set the name of the machine')
def update(id, size, instance_type, name):
    """
    Update instance specifications
    """
    session = get_session()
    ec2_resource = session.resource('ec2')
    ec2_client = session.client('ec2')

    instance = ec2_resource.Instance(id=id)

    if name:
        print(f"Updating instance name to: {name}...")
        instance.create_tags(
            Tags=[
                {
                    "Key": "Name",
                    "Value": name,
                }
            ]
        )

    if size:
        print(f"Updating disk size to: {size}...")
        if instance.block_device_mappings:
            root_volume_id = instance.block_device_mappings[0]['Ebs']['VolumeId']
            response = ec2_client.modify_volume(
                VolumeId=root_volume_id,
                Size=size
            )
            status = response['VolumeModification']['ModificationState']
            print(f"Disk is currently in {status} state. It may take a few minutes for the size change to finish")
        else:
            print("No disk attached to this instance")

    if instance_type:
        print(f"Updating instance type to: {instance_type}...")
        if instance.state['Name'] != 'stopped':
            print(f"Instance must be in stopped state to change type. Current state: {instance.state['Name']}")
            exit(1)

        instance.modify_attribute(
            InstanceType={
                "Value": instance_type
            }
        )

    instance.reload()
    print_machine_info([instance])