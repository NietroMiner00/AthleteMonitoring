import json
import yaml
from accesslink import AccessLink
from API import API

CALLBACK_PORT = 5000
CALLBACK_ENDPOINT = "/oauth2_callback"

CONFIG_FILENAME = "config.yml"

REDIRECT_URL = "http://localhost:{}{}".format(CALLBACK_PORT, CALLBACK_ENDPOINT)


def load_config(filename):
    """Load configuration from a yaml file"""
    try:
        with open(filename) as f:
            return yaml.load(f, yaml.Loader)
    except FileNotFoundError:
        with open(filename, "a+") as f:
            config = {
                "access_token": "",
                "client_id": "",
                "client_secret": "",
                "refresh_token": ""
            }
            yaml.safe_dump(config, f, default_flow_style=False)

            return None

def save_config(config, filename):
    """Save configuration to a yaml file"""
    with open(filename, "w+") as f:
        yaml.safe_dump(config, f, default_flow_style=False)

def pretty_print_json(data):
    print(json.dumps(data, indent=4, sort_keys=True))

config = load_config(CONFIG_FILENAME)
if config == None or config['client_id'] == None or config['client_secret'] == None:
    print("Insert clientID and secret into config.yml")
    exit()

accesslink = AccessLink(client_id=config['client_id'],
                        client_secret=config['client_secret'],
                        redirect_url=REDIRECT_URL)

api = API()