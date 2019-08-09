import click

from infinity.aws.auth import get_session


def get_value_for_quota_name(quotas, quota_name):
    for quota in quotas:
        if quota['QuotaName'] == quota_name:
            return quota['Value']
    return None


@click.command()
@click.option('--instance-type', required=True, type=str)
def quota(instance_type):
    """
    Show the quota limit
    """
    quota_client = get_session().client('service-quotas')
    quota_paginator_client = quota_client.get_paginator('list_aws_default_service_quotas')

    quota_name = f"Running On-Demand {instance_type} instances"
    next_token = None
    quota_value = None

    pagination_config = {
        'MaxItems': 100,
    }

    while True:
        # response = quota_client.list_service_quotas(
        #     ServiceCode='ec2',
        #     MaxResults=100,
        #     NextToken=next_token,
        # )

        if next_token:
            pagination_config['StartingToken'] = next_token

        response = quota_paginator_client.paginate(
            ServiceCode='ec2',
        )

        quotas = response
        quota_value = get_value_for_quota_name(quotas, quota_name)
        next_token = response['NextToken']
        print(quota_value, next_token)

        # Quota value is found
        if quota_value:
            break

        # Quota pagination is done
        if not next_token:
            break

    print(quota_value)