import boto3

from infinity.settings import get_infinity_settings


session = None


def get_session():
    global session
    if not session:
        session = boto3.Session(region_name=get_infinity_settings()['aws_region_name'],
                                profile_name=get_infinity_settings()['aws_profile_name'])

    return session