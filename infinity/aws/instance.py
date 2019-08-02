from infinity.aws.exceptions import AWSInstanceNotFound


def get_infinity_instances(session):
    ec2 = session.resource('ec2')
    custom_filter = [{
        'Name': 'tag:type',
        'Values': ['infinity']
    }]
    instances = ec2.instances.filter(Filters=custom_filter)
    return instances


def get_specific_instance(session, id):
    ec2 = session.resource('ec2')
    instances = list(ec2.instances.filter(InstanceIds=[id]))
    if len(instances) == 0:
        raise AWSInstanceNotFound(f"No instance found for id: {id}")
    return instances[0]