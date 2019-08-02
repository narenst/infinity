import boto3

session = None


def get_session():
    global session
    if not session:
        session = boto3.Session(profile_name='floyd-dev')

    return session