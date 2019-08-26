import click

from infinity.aws.auth import get_session
from infinity.settings import get_infinity_settings


def get_value_for_quota_name(quotas, quota_name):
    for quota in quotas:
        if quota['QuotaName'] == quota_name:
            return quota['Value'], quota['QuotaCode']
    return None, None


@click.command()
@click.option('--instance-type', required=True, type=str)
@click.option('--increase-to', type=int)
def quota(instance_type, increase_to):
    """
    View and increase quota limit for your account.

    This command shows the current quota limit for the instance type in your account.
    You will not be able to spin up more than the quota number of instances.
    To increase the quota limit, you can request AWS with this command as well.
    """
    quota_client = get_session().client('service-quotas')
    quota_paginator_client = quota_client.get_paginator('list_service_quotas')

    quota_name = f"Running On-Demand {instance_type} instances"
    response = quota_paginator_client.paginate(
        ServiceCode='ec2',
    )

    for quota_set in response:
        quota_value, quota_code = get_value_for_quota_name(quota_set['Quotas'], quota_name)
        if quota_value is not None:
            quota_value = int(quota_value)
            break

    aws_region = get_infinity_settings()['aws_region_name']
    if quota_value is None:
        print("Cannot find quota for this instance type. Double check if the type value is accurate")
        exit(1)

    print(f"Your quota limit for {instance_type} in the {aws_region} region is: {quota_value}")

    # Get any pending increase request for this instance type:
    response = quota_client.list_requested_service_quota_change_history_by_quota(
        ServiceCode='ec2',
        QuotaCode=quota_code,
    )
    for request in response['RequestedQuotas']:
        if request['Status'] in ['PENDING', 'CASE_OPENED']:
            print(f"You have a pending quota request increase to limit: {request['DesiredValue']}")
            # Exit if there is an open or pending request, cannot request another one
            exit(0)

    # Process quota increase now
    if increase_to:
        if increase_to <= quota_value:
            print(f"New quota limit {increase_to} is less than or equal to current limit: {quota_value}")
            exit(1)

        quota_client.request_service_quota_increase(
            ServiceCode='ec2',
            QuotaCode=quota_code,
            DesiredValue=float(increase_to)
        )
        print(f"Submitted a quota increase request for {instance_type} in the {aws_region} region to: {increase_to}")