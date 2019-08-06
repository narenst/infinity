import click

from infinity.aws.auth import get_session
from infinity.aws.instance import get_specific_instance
from infinity.command.list import print_machine_info


@click.command()
@click.argument('id')
def start(id):
    """
    Start the cloud machine with the id
    """
    session = get_session()
    instance = get_specific_instance(session=session, id=id)

    instance_state = instance.state['Name']
    if instance_state != 'stopped':
        raise Exception(f"Instance is not in stopped state: {instance_state}")

    print("Starting instance now...")
    instance.start()

    print("Waiting for the instance to be up and running...")
    instance.wait_until_running()

    instance.reload()
    if instance.state['Name'] == 'running':
        print("Machine is started")
    else:
        raise Exception(f"Error starting the instance: {id}")

    print_machine_info(instance)