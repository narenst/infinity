import random
import string
from time import sleep
import click
from dateutil.parser import parse

from infinity.aws.auth import get_session
from infinity.command.list import print_machine_info
from infinity.settings import get_infinity_settings, CONFIG_FILE_PATH


def get_latest_deep_learning_ami():
    image_description = "Deep Learning AMI (Ubuntu) Version*"
    client = get_session().client('ec2')
    response = client.describe_images(
        Filters=[
            {
                'Name': 'name',
                'Values': [
                    image_description
                ]
            },
            {
                'Name': 'owner-alias',
                'Values': [
                    'amazon'
                ]
            }
        ]
    )
    images = response['Images']
    images_created_map = {}
    for image in images:
        images_created_map[image['ImageId']] = parse(image['CreationDate'])

    latest_ami = max(images_created_map.items(), key=lambda x: x[1])[0]
    return latest_ami


@click.command()
def create():
    """
    Create a new cloud machine with default specs
    """
    session = get_session()
    client = session.client('ec2')
    infinity_settings = get_infinity_settings()

    # Spot instance request parameters
    machine_name_suffix = ''.join(random.choice(string.ascii_lowercase) for x in range(10))

    # Pick the machine image
    ami = infinity_settings['aws_ami']
    if not ami:
        print("No ami specified in the configuration. Finding the latest Deep learning ami ")
        ami = get_latest_deep_learning_ami()

    if not ami:
        print(f"No AMI found, please specify the ami to use in the infinity config file: {CONFIG_FILE_PATH}")
        exit(1)

    instance_type = infinity_settings['default_aws_instance_type'] or 'p2.xlarge'

    response = client.run_instances(
        ImageId=ami,
        InstanceType=instance_type,
        KeyName=infinity_settings.get('aws_key_name'),
        BlockDeviceMappings=[
            {
                'DeviceName': '/dev/sda1',
                'Ebs': {
                    'DeleteOnTermination': False,
                },
            }
        ],
        EbsOptimized=True,
        SecurityGroupIds=[
            infinity_settings.get('aws_security_group_id'),
        ],
        SubnetId=infinity_settings.get('aws_subnet_id'),
        MaxCount=1,
        MinCount=1,
        TagSpecifications=[
            {
                "ResourceType": "instance",
                "Tags": [
                    {
                        "Key": "Name",
                        "Value": f"infinity-{machine_name_suffix}"
                    },
                    {
                        "Key": "type",
                        "Value": "infinity"
                    }
                ]
            }
        ]
    )

    instance_id = response['Instances'][0]['InstanceId']

    # Wait until the new instance ID is propagated
    sleep(1)

    # Get the instance volume id
    ec2_resource = session.resource('ec2')

    ec2_instance = ec2_resource.Instance(instance_id)
    root_volume_id = ec2_instance.block_device_mappings[0]['Ebs']['VolumeId']

    # Tag the disk volume
    client.create_tags(
        Resources=[root_volume_id],
        Tags=[
            {
                'Key': 'type',
                'Value': 'infinity'
            },
            {
                'Key': 'Name',
                'Value': f'infinity-{machine_name_suffix}'
            }
        ]
    )

    # Wait for the instance to be running again
    while ec2_instance.state == 'pending':
        print(f"Instance id: {ec2_instance.id}, state: {ec2_instance.state}")
        ec2_instance.reload()

    print_machine_info([ec2_instance])