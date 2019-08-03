import click

from infinity.aws.auth import get_session
from infinity.aws.instance import get_specific_instance


@click.command()
def create(id):
    """
    Create a new cloud machine with default specs
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