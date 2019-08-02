import click

from infinity.aws.auth import get_session
from infinity.aws.instance import get_specific_instance


@click.command()
@click.argument('id', nargs=1)
def stop(id):
    """
    Stop the cloud machine with the id
    """
    session = get_session()
    instance = get_specific_instance(session=session, id=id)

    instance_state = instance.state['Name']
    if instance_state != 'running':
        raise Exception(f"Instance is not in running state: {instance_state}")

    print("Stopping instance now...")
    instance.stop()

    print("Waiting for the instance to be stopped...")
    instance.wait_until_stopped()

    instance.reload()
    if instance.state['Name'] == 'stopped':
        print("Machine is stopped")
    else:
        raise Exception(f"Error stopping the instance: {id}")