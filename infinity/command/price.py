import sys
import click
import boto3
import requests
from datetime import datetime
from tabulate import tabulate

from infinity.aws.auth import get_session
from infinity.settings import get_infinity_settings


progress_counter = 0
PROGRESS_CHARS = ['|', '/', '-', '\\']
SPOT_ADVISOR_DATA_URL = 'https://spot-bid-advisor.s3.amazonaws.com/spot-advisor-data.json'
ONDEMAND_INSTANCE_PRICE_URL = 'http://www.ec2instances.info/instances.json'


def print_progress():
    global progress_counter
    sys.stdout.write(PROGRESS_CHARS[progress_counter % len(PROGRESS_CHARS)])
    progress_counter += 1
    sys.stdout.flush()
    sys.stdout.write('\r')


def get_interruption_frequency_for_instance_type(instance_type):
    response = requests.get(SPOT_ADVISOR_DATA_URL)
    data = response.json()

    region_interrupt_map = {}
    interrupt_percent_reference = {item['index']: item for item in data['ranges']}
    for region_name in data['spot_advisor']:
        interrupt_info = data['spot_advisor'][region_name]['Linux'].get(instance_type)
        if not interrupt_info:
            continue
        interrupt_index = interrupt_info['r']
        region_interrupt_map[region_name] = interrupt_percent_reference[interrupt_index]['label']

    return region_interrupt_map


def get_on_demand_instance_pricing(instance_type):
    response = requests.get(ONDEMAND_INSTANCE_PRICE_URL)
    data = response.json()

    region_on_demand_price_map = {}
    for item in data:
        if item['instance_type'] == instance_type:
            for region_name in item['pricing']:
                on_demand_price = item['pricing'][region_name].get('linux')
                if on_demand_price:
                    region_on_demand_price_map[region_name] = on_demand_price.get('ondemand')

    return region_on_demand_price_map


@click.command()
@click.option('--instance-type', required=True, type=str)
def price(instance_type):
    """
    View the spot and on-demand prices for the instance across all AWS regions.

    This command queries the spot instance price for every region that offers the instance.
    It also gets the probability that the machine will be preempted. For completeness, it also
    shows the on-demand price for comparison.
    """
    client = get_session().client('ec2')

    response = client.describe_regions()
    regions = [item['RegionName'] for item in response['Regions']]
    regions.sort()

    print("Getting On-demand prices across regions ...")
    region_on_demand_price = get_on_demand_instance_pricing(instance_type)
    print("Getting frequency of interruptions for spot instances ...")
    interruption_frequency = get_interruption_frequency_for_instance_type(instance_type)
    print("Getting real-time price of Spot instances ...")

    spot_price_table = []
    for region in regions:
        print_progress()
        session = boto3.Session(region_name=region, profile_name=get_infinity_settings()['aws_profile_name'])
        client = session.client('ec2')

        response = client.describe_availability_zones()
        azs = [item['ZoneName'] for item in response['AvailabilityZones']]

        spot_price_entries = []
        for az in azs:
            print_progress()
            response = client.describe_spot_price_history(
                InstanceTypes=[instance_type],
                MaxResults=5,
                StartTime=datetime.utcnow(),
                EndTime=datetime.utcnow(),
                AvailabilityZone=az,
                ProductDescriptions=[
                    "Linux/UNIX",
                ]
            )
            spot_price_history = response['SpotPriceHistory']
            if not spot_price_history:
                continue

            spot_price = spot_price_history[0]['SpotPrice']
            on_demand_price = region_on_demand_price.get(region, 'N/A')
            interrupt_freq = interruption_frequency.get(region, 'N/A')
            spot_price_entries.append([region, az, on_demand_price, spot_price, interrupt_freq])

        if spot_price_entries:
            spot_price_table = spot_price_table + spot_price_entries + ['']

    table_header = ['REGION', 'AVAILABILITY ZONE', 'ON-DEMAND PRICE (USD)', 'SPOT PRICE (USD)', 'FREQ OF INTERRUPTION']
    print(tabulate(spot_price_table,
                   headers=table_header,
                   tablefmt='psql',
                   colalign=['left', 'left', 'decimal', 'decimal', 'center']))