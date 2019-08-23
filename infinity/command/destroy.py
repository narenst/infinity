import click

from infinity.aws.auth import get_session
from infinity.command.list import print_machine_info


@click.command()
@click.argument('id')
@click.option('--delete-disk/--no-delete-disk', default=True, help="Skip deleting the root disk")
def destroy(id, delete_disk):
    """
    Terminate the cloud machine with the id. This is irrecoverable
    """
    ec2_resource = get_session().resource('ec2')
    instance = ec2_resource.Instance(id)

    # Set if the root volume should be deleted on termination
    instance.modify_attribute(
        BlockDeviceMappings=[
            {
                'DeviceName': '/dev/sda1',
                'Ebs': {
                    'DeleteOnTermination': delete_disk,
                },
            }
        ]
    )

    root_disk_delete_status = "delete" if delete_disk else "keep"  # noqa
    if click.confirm("\nAre you sure you want to destroy the machine? This is irrrecoverable. "
                     f"And you have to chosen to {root_disk_delete_status} the root disk."):

        print("Destroying instance now...")
        ec2_client = get_session().client('ec2')
        ec2_client.terminate_instances(
            InstanceIds=[
                id,
            ]
        )

        print("Removing alerts")
        cloudwatch_client = get_session().client('cloudwatch')
        cloudwatch_client.delete_alarms(
            AlarmNames=[
                f'uptime-alarm-for-{id}'
            ]
        )

        instance.reload()
        print_machine_info([instance])