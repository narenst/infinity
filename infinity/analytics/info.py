import uuid


def generate_user_id():
    return str(uuid.uuid1())