import boto3

session = None


def get_session():
    global session
    if not session:
        session = boto3.Session(region_name='us-east-2', profile_name='floyd-dev')

    return session