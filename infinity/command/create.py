import random
import string
from time import sleep
import click
import os
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


def subscribe_email_to_instance_notifications(session, notification_email):
    """
    Create an SNS topic or get the already created topic.
    Add a new subscription to this topic for the email
    """
    sns_client = session.client('sns')

    # Get the topic arn
    response = sns_client.create_topic(
        Name='infinity-notifications',
        Attributes={
            'DisplayName': 'infinity-notifications',
        },
        Tags=[
            {
                'Key': 'type',
                'Value': 'infinity'
            }
        ]
    )

    topic_arn = response['TopicArn']

    # Check if subscription is alredy added to this email
    # Note: This checks only the first 100 subscriptions
    # This should be fine since we do not expect so many emails for this
    response = sns_client.list_subscriptions_by_topic(
        TopicArn=topic_arn,
    )
    existing_subscriptions = response['Subscriptions']
    for subscription in existing_subscriptions:
        if subscription['Endpoint'] == notification_email:
            return topic_arn

    # Create new email subscription
    response = sns_client.subscribe(
        TopicArn=topic_arn,
        Protocol='email',
        Endpoint=notification_email,
    )

    return topic_arn


def create_cloudwatch_alert_for_instance(session, instance_id, topic_arn):
    """
    Create simple aliveness alert for instance.
    It should trigger an Alarm with notification to the `infinity-notifications` topic
    Alarm checks every 15 minutes. And triggers after 12 hours of uptime.
    """
    cloudwatch_client = session.client('cloudwatch')

    cloudwatch_client.put_metric_alarm(
        AlarmName=f'uptime-alarm-for-{instance_id}',
        AlarmDescription=f'Alert when the instance {instance_id} is running for more than 12 hours',
        ComparisonOperator='LessThanOrEqualToThreshold',
        MetricName='CPUUtilization',
        Namespace='AWS/EC2',
        EvaluationPeriods=72, #144,
        Period=300,
        Statistic='Average',
        Threshold=100.0,
        ActionsEnabled=False,
        TreatMissingData='notBreaching',
        Dimensions=[
            {
                'Name': 'InstanceId',
                'Value': instance_id
            },
        ],
        AlarmActions=[
            topic_arn,
        ]
    )


@click.command()
@click.option('--spot/--on-demand', 'is_spot', default=False)
@click.option('--attach-volume-id', type=str, help="ID of secondary volume to attach")
@click.option('--notification-email', type=str, help="Email address to send notifications to. This is only sent to AWS SNS service")
def create(is_spot, attach_volume_id, notification_email):
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

    print(f"Using ami: {ami}")
    instance_type = infinity_settings['default_aws_instance_type'] or 'p2.xlarge'

    if is_spot:
        instance_market_options = {
            'MarketType': 'spot',
            'SpotOptions': {
                'SpotInstanceType': 'one-time',
            }
        }
    else:
        instance_market_options = {}

    user_data_file_path = os.path.join(os.path.dirname(__file__), 'user_data.sh')
    with open(user_data_file_path, 'r') as f:
        user_data = f.read()

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
        InstanceMarketOptions=instance_market_options,
        UserData=user_data,
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

    # Add email address to SNS Queue and setup alert
    if notification_email:
        topic_arn = subscribe_email_to_instance_notifications(session=session,
                                                              notification_email=notification_email)

        create_cloudwatch_alert_for_instance(session=session,
                                             instance_id=instance_id,
                                             topic_arn=topic_arn)

    # Wait for the instance to be running again
    while ec2_instance.state == 'pending':
        print(f"Instance id: {ec2_instance.id}, state: {ec2_instance.state}")
        ec2_instance.reload()

    print_machine_info([ec2_instance])

    print("\nHow was your experience setting up your machine? "
          "Anything we should improve?: https://github.com/narenst/infinity/issues/new")
