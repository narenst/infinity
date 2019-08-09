import yaml
import os


CONFIG_FILE_PATH = os.path.expanduser('~/.infinity/settings.yaml')
DEFAULT_CONFIG = {
    "aws_region_name": "us-west-2",
    "aws_profile_name": "default",
    "aws_key_name": "InfinitySSH",
    "aws_stack_name": "InfinityStack",
    "aws_security_group_id": None,
    "aws_subnet_id": None,
}


def get_infinity_settings():
    if os.path.exists(CONFIG_FILE_PATH):
        with open(CONFIG_FILE_PATH, 'r') as config_file:
            config = yaml.safe_load(config_file)
            return config
    else:
        return DEFAULT_CONFIG


def update_infinity_settings(key_value_pairs):
    if os.path.exists(CONFIG_FILE_PATH):
        with open(CONFIG_FILE_PATH, 'r') as config_file:
            config = yaml.safe_load(config_file)

        config.update(key_value_pairs)

        with open(CONFIG_FILE_PATH, 'w') as config_file:
            config_file.write("""
##########################################################
# Settings for Infinity Client
# These values are set by running "infinity setup" command
# Overwrite them if you already have an AWS setup
##########################################################\n
""")
            yaml.safe_dump(config, config_file)