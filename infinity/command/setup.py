import click
import boto3
from botocore.exceptions import ClientError
import os
from shutil import copyfile

from infinity.settings import (get_infinity_settings, update_infinity_settings,
                               CONFIG_FILE_PATH, CLOUD_FORMATION_FILE_PATH)


@click.command()
@click.argument('region-name', required=True)
@click.option('--aws-profile', default='default')
@click.option('--cloud-formation-file',
              type=click.Path(exists=True, readable=True, resolve_path=True))
@click.option('--ssh-public-key-path',
              'ssh_public_key',
              required=True,
              type=click.File(mode='r'),
              help="Path to the SSH public key, will be uploaded to AWS")
@click.option('--ssh-private-key-path',
              required=True,
              type=click.Path(exists=True, resolve_path=True))
@click.option('--notification-email',
              type=str,
              help="Email address to send notifications to. This is only sent to AWS SNS service")
def setup(region_name, aws_profile, cloud_formation_file, ssh_public_key, ssh_private_key_path, notification_email):
    """
    Sets up infinity before first run.

    Before you run Infinity for the first time, you need to run this command. It creates a
    CloudFormation stack. And uploads a SSH key to AWS to connect to the instances
    you will create. Infinity config is stored in the config file stored at ~/.infinity/settings.yaml.
    """
    session = boto3.Session(region_name=region_name,
                            profile_name=aws_profile)
    cf_client = session.client('cloudformation')
    stack_name = get_infinity_settings().get('aws_stack_name')
    key_name = get_infinity_settings().get('aws_key_name')

    # Check if infinity stack already exists
    try:
        stacks = cf_client.describe_stacks(StackName=stack_name)
        if stacks:
            print("Infinity stack already exists")
    except ClientError:
        # Error expected if Stack does not exist
        # Create a new stack
        if not cloud_formation_file:
            print(f"Using default AWS cloudformation from: {CLOUD_FORMATION_FILE_PATH}")
            if not os.path.exists(CLOUD_FORMATION_FILE_PATH):
                copyfile(os.path.join(os.path.dirname(__file__), 'infinity_cloudformation.yaml'),
                         CLOUD_FORMATION_FILE_PATH)
            cloud_formation_file = CLOUD_FORMATION_FILE_PATH

        print(f"Setting up a new Infinity stack in {region_name}")
        with open(cloud_formation_file, 'r') as cf_template:
            _ = cf_client.create_stack(
                StackName=stack_name,
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
        waiter.wait(StackName=stack_name)

        print("Infinity stack created successfully")

        # Get the configuration from the new stack
        stacks_response = cf_client.describe_stacks(StackName=stack_name)['Stacks'][0]
        output_map = {item['OutputKey']: item['OutputValue'] for item in stacks_response['Outputs']}

        settings_update = {
            "aws_region_name": region_name,
            "aws_profile_name": aws_profile,
            "aws_subnet_id": output_map['InfinitySubnetID'],
            "aws_security_group_id": output_map['InfinitySecurityGroupID'],
        }

        update_infinity_settings(settings_update)
        print(f"Infinity config file is updated with the new stack info: {CONFIG_FILE_PATH}")

    # Create Key Pair
    ec2_client = session.client('ec2')
    try:
        ec2_client.describe_key_pairs(
            KeyNames=[
                key_name
            ]
        )
        print("SSH Public key already exists")
    except ClientError:
        # SSH Key not found, so upload
        print("Uploading Public SSH Key")
        ec2_client.import_key_pair(
            KeyName=key_name,
            PublicKeyMaterial=ssh_public_key.read()
        )
        print("SSH Public Key uploaded")

        settings_update = {
            "ssh_private_key_path": ssh_private_key_path,
        }

        update_infinity_settings(settings_update)
        print(f"Infinity config file is updated with the new key info: {CONFIG_FILE_PATH}")

    # Set notification email
    if not notification_email:
        notification_email = click.prompt(
            'Please enter an email address to send instance notifications from AWS. Press enter to skip this',
            type=str,
            default=None,
        )

    if notification_email:
        update_infinity_settings(
            {
                "notification_email": notification_email
            }
        )
        print(f"Infinity config file is updated with the notification email: {CONFIG_FILE_PATH}")

    print("\nHow was your setup experience? Please share your feedback here: "
          "https://github.com/narenst/infinity/issues/new")