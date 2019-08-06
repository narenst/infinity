import random
import string
from time import sleep
import click

from infinity.aws.auth import get_session


@click.command()
def create():
    """
    Create a new cloud machine with default specs
    """
    session = get_session()
    client = session.client('ec2')

    # Spot instance request parameters
    response = client.request_spot_instances(
        InstanceCount=1,
        LaunchSpecification={
            'ImageId': 'ami-0ddba16a97b1dcda5',
            'InstanceType': 'p2.xlarge',
            'KeyName': 'naren-aws',
            'Placement': {
                'AvailabilityZone': 'us-west-2c'
            },
            'BlockDeviceMappings': [
                {
                    'DeviceName': '/dev/sda1',
                    'Ebs': {
                        'DeleteOnTermination': False,
                    },
                }
            ],
            'EbsOptimized': True,
            'SecurityGroupIds': [
                'sg-0dae15838d442bcbd',
            ],
        },
        Type='one-time'
    )

    spot_request_id = response['SpotInstanceRequests'][0]['SpotInstanceRequestId']
    # Wait until the new instance ID is propagated
    sleep(1)

    # Tag the request next
    client.create_tags(
        Resources=[spot_request_id],
        Tags=[
            {
                'Key': 'type',
                'Value': 'infinity'
            }
        ]
    )

    # Wait for the spot request to be fulfilled
    spot_request_details = None
    spot_request_state = 'open'

    for _ in range(60):
        spot_instance_requests = client.describe_spot_instance_requests(
            SpotInstanceRequestIds=[
                spot_request_id,
            ]
        )
        spot_request_details = spot_instance_requests['SpotInstanceRequests'][0]
        spot_request_state = spot_request_details['State']

        print(f"Spot id: {spot_request_id}, Status: {spot_request_state}")
        if spot_request_state != 'open':
            break

        # Wait for a second before trying again
        sleep(1)
    else:
        # Cancel the spot request
        client.cancel_spot_instance_requests(
            SpotInstanceRequestIds=[
                spot_request_id,
            ]
        )
        print(f"Cancelled the spot instance request id: {spot_request_id}. "
              "Please try again after sometime, or try with a different regions, AZ, or machine spec")
        exit(1)

    if spot_request_state != 'active':
        print(f"Spot Instance was not allocated: {spot_request_state}, Status: {spot_request_details['Status']}")
        exit(1)

    spot_instance_id = spot_request_details['InstanceId']

    # Get instance volume id
    ec2_resource = session.resource('ec2')

    ec2_instance = ec2_resource.Instance(spot_instance_id)
    root_volume_id = ec2_instance.block_device_mappings[0]['Ebs']['VolumeId']

    # Tag the instance and disk volume
    machine_name_suffix = ''.join(random.choice(string.lowercase) for x in range(10))
    client.create_tags(
        Resources=[spot_instance_id, root_volume_id],
        Tags=[
            {
                'Key': 'type',
                'Value': 'infinity'
            },
            {
                'Name': 'Name',
                'Value': f'infinity-{machine_name_suffix}'
            }
        ]
    )

    # Wait for the instance to be running again
    while ec2_instance.state == 'pending':
        print(f"Instance id: {ec2_instance.id}, state: {ec2_instance.state}")
        ec2_instance.reload()

    print(f"Instance id: {ec2_instance.id}, state: {ec2_instance.state}")