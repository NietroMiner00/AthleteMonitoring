#!/usr/bin/env python

from .oauth2 import OAuth2Client
import requests
from requests.models import HTTPBasicAuth
import utils

AUTHORIZATION_URL = "https://auth.polar.com/oauth/authorize"
ACCESS_TOKEN_URL = "https://auth.polar.com/oauth/token"
ACCESSLINK_URL = "https://admin.polaraccesslink.com/"


class AccessLink(object):
    """Wrapper class for Polar Open AccessLink API v3"""

    def __init__(self, client_id, client_secret, redirect_url=None):
        if not client_id or not client_secret:
            raise ValueError("Client id and secret must be provided.")

        self.oauth = OAuth2Client(url=ACCESSLINK_URL,
                                  authorization_url=AUTHORIZATION_URL,
                                  access_token_url=ACCESS_TOKEN_URL,
                                  redirect_url=redirect_url,
                                  client_id=client_id,
                                  client_secret=client_secret)

    @property
    def authorization_url(self):
        """Get the authorization url for the client"""
        return self.oauth.get_authorization_url()

    def get_access_token(self, refresh=True, authorization_code=""):
        """Request access token for a user.

        :param authorization_code: authorization code received from authorization endpoint.
        """
        if refresh:
            access_token = requests.post(f"https://auth.polar.com/oauth/token?refresh_token={ utils.config['refresh_token'] }&grant_type=refresh_token", auth=HTTPBasicAuth(utils.config['client_id'], utils.config['client_secret'])).json()['access_token']
            utils.config['access_token'] = access_token
            utils.save_config(utils.config, utils.CONFIG_FILENAME)
            return access_token
        else:
            token_response = self.oauth.get_access_token(authorization_code)
            utils.config["refresh_token"] = token_response["refresh_token"]
            utils.config["access_token"] = token_response["access_token"]
            utils.save_config(utils.config, utils.CONFIG_FILENAME)
            return token_response["access_token"]
