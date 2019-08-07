import click
import boto3
from botocore.exceptions import ClientError


@click.command()
@click.argument('region-name')
@click.option('--aws-profile', default=None)
@click.option('--cloud-formation-file',
              required=True,
              type=click.Path(exists=True, readable=True, resolve_path=True))
@click.option('--ssh-public-key',
              required=True,
              type=click.File(mode='r'))
def setup(region_name, aws_profile, cloud_formation_file, ssh_public_key):
    """
    Sets up the required AWS components for running infinity
    """
    session = boto3.Session(region_name=region_name,
                            profile_name=aws_profile)
    cf_client = session.client('cloudformation')

    # Check if infinity stack already exists
    try:
        stacks = cf_client.describe_stacks(StackName='InfinityStack')
        if stacks:
            print("Infinity stack already exists")
    except ClientError:
        # Error expected if Stack does not exist

        # Create a new stack
        with open(cloud_formation_file, 'r') as cf_template:
            _ = cf_client.create_stack(
                StackName='InfinityStack',
                TemplateBody=cf_template.read(),
                Tags=[
                    {
                        'Key': 'type',
                        'Value': 'infinity'
                    }
                ]
            )

        # Wait for the stack to be created
        waiter = cf_client.get_waiter('stack_create_complete')
        waiter.wait(StackName='InfinityStack')

        print("Infinity stack created successfully")

    # Create Key Pair
    ec2_client = session.client('ec2')
    try:
        ec2_client.describe_key_pairs(
            KeyNames=[
                'InfinitySSH'
            ]
        )
    except ClientError:
        # SSH Key not found, so upload
        print("Uploading Public SSH Key")
        ec2_client.import_key_pair(
            KeyName='InfinitySSH',
            PublicKeyMaterial=ssh_public_key.read()
        )
        print("SSH Public Key uploaded")