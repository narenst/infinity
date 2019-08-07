import click
import boto3
from botocore.exceptions import ClientError

from infinity.settings import get_infinity_settings


@click.command()
def teardown():
    """
    Deletes all the AWS components created by Infinity
    """
    infinity_settings = get_infinity_settings()

    session = boto3.Session(region_name=infinity_settings.get('aws_region_name'),
                            profile_name=infinity_settings.get('aws_profile_name'))
    cf_client = session.client('cloudformation')
    stack_name = infinity_settings.get('aws_stack_name')
    key_name = infinity_settings.get('aws_key_name')

    # Check if infinity stack already exists
    try:
        cf_client.describe_stacks(StackName=stack_name)
    except ClientError:
        print("Infinity Stack does not exist, nothing to teardown")
        exit(1)

    if click.confirm("\nAre you sure you want to destroy the Infinity setup? This is irrrecoverable."):
        # Delete the stack
        cf_client.delete_stack(
            StackName=stack_name,
        )

        print("Stack delete is initiated ...")
        # Wait for the stack to be created
        waiter = cf_client.get_waiter('stack_delete_complete')
        waiter.wait(StackName=stack_name)

        print("Infinity Stack deleted successfully")

        print("Deleting the public SSH Key")
        ec2_client = session.client('ec2')
        ec2_client.delete_key_pair(
            KeyName=key_name,
        )