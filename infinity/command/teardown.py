import click
import boto3
from botocore.exceptions import ClientError


@click.command()
@click.argument('region-name')
@click.option('--aws-profile', default=None)
def teardown(region_name, aws_profile):
    """
    Deletes all the AWS components created by Infinity
    """
    session = boto3.Session(region_name=region_name,
                            profile_name=aws_profile)
    cf_client = session.client('cloudformation')

    # Check if infinity stack already exists
    try:
        cf_client.describe_stacks(StackName='InfinityStack')
    except ClientError:
        print("Infinity Stack does not exist, nothing to teardown")
        exit(1)

    if click.confirm("\nAre you sure you want to destroy the Infinity setup? This is irrrecoverable."):
        # Delete the stack
        cf_client.delete_stack(
            StackName='InfinityStack',
        )

        print("Stack delete is initiated ...")
        # Wait for the stack to be created
        waiter = cf_client.get_waiter('stack_delete_complete')
        waiter.wait(StackName='InfinityStack')

        print("Infinity Stack deleted successfully")

        print("Deleting the public SSH Key")
        ec2_client = session.client('ec2')
        ec2_client.delete_key_pair(
            KeyName='InfinitySSH',
        )