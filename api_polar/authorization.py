#!/usr/bin/env python
from __future__ import print_function

import requests
from requests.auth import HTTPBasicAuth

from flask import Flask, request, redirect

from utils import load_config, save_config
from accesslink import AccessLink
from accesslink.oauth2 import OAuth2Client


CALLBACK_PORT = 5000
CALLBACK_ENDPOINT = "/oauth2_callback"

CONFIG_FILENAME = "config.yml"

REDIRECT_URL = "http://localhost:{}{}".format(CALLBACK_PORT, CALLBACK_ENDPOINT)

config = load_config(CONFIG_FILENAME)

if 'refresh_token' in config.keys():
    access_token = requests.post(f"https://auth.polar.com/oauth/token?refresh_token={ config['refresh_token'] }&grant_type=refresh_token", auth=HTTPBasicAuth(config['client_id'], config['client_secret'])).json()['access_token']
    config['access_token'] = access_token
    save_config(config, "config.yml")
    exit()

accesslink = AccessLink(client_id=config['client_id'],
                        client_secret=config['client_secret'],
                        redirect_url=REDIRECT_URL)


app = Flask(__name__)


@app.route("/")
def authorize():
    print('zeile 38 ' + accesslink.authorization_url)
    print(type(accesslink.authorization_url))
    index = accesslink.authorization_url.find('redirect_uri')
    neuer_link = str(accesslink.authorization_url)[0:index]
    neuer_link = neuer_link + 'scope=team_read'
    print('neuer link: ' + neuer_link)
    #return redirect(accesslink.authorization_url)
    return redirect(neuer_link)


@app.route(CALLBACK_ENDPOINT)
def callback():
    """Callback for OAuth2 authorization request
    Saves the user's id and access token to a file.
    """

    #
    # Get authorization from the callback request parameters
    #
    authorization_code = request.args.get("code")
    print('auth code' + authorization_code)

    #
    # Get an access token for the user using the authorization code.
    #
    # The authorization code is only valid for 10 minutes, so the access token
    # should be fetched immediately after the authorization step.
    #
    token_response = accesslink.get_access_token(authorization_code)
    print('_________')
    print(token_response)

    #
    # Save the user's id and access token to the configuration file.
    #
    config["refresh_token"] = token_response["refresh_token"]
    config["access_token"] = token_response["access_token"]
    save_config(config, CONFIG_FILENAME)

    exit()
    return "Client authorized! You can now close this page."


def main():
    print("Navigate to http://localhost:{port}/ for authorization.\n".format(port=CALLBACK_PORT))
    app.run(host='localhost', port=CALLBACK_PORT)


if __name__ == "__main__":
    main()