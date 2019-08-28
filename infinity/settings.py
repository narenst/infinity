import yaml
import os
from shutil import copyfile


CONFIG_FILE_DIR = os.path.expanduser('~/.infinity')
CONFIG_FILE_PATH = os.path.join(CONFIG_FILE_DIR, 'settings.yaml')
CLOUD_FORMATION_FILE_PATH = os.path.expanduser('~/.infinity/infinity_cloudformation.yaml')


def get_infinity_settings():
    if not os.path.exists(CONFIG_FILE_PATH):
        os.makedirs(CONFIG_FILE_DIR, exist_ok=True)
        copyfile(os.path.join(os.path.dirname(__file__), 'settings.yaml'), CONFIG_FILE_PATH)

    with open(CONFIG_FILE_PATH, 'r') as config_file:
        config = yaml.safe_load(config_file)
        return config


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
    else:
        raise Exception(f"Infinity Settings file not found at: {CONFIG_FILE_PATH}")