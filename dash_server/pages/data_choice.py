from threading import local
import dash as ds
from dash import dependencies
from dash import html
from dash import dcc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from requests.models import HTTPBasicAuth
from utils import load_config, save_config, CONFIG_FILENAME, accesslink
import requests
from accesslink import AccessLink

from app import app
from pages import localdata

layout = html.Div([
    html.H3('Datatype'),
    #Dropdown with either Local or Polar option
    dcc.Dropdown(
        id='data_dropdown',
        options=[
            {'label': 'Local (.csv/.xls/...)', 'value': 'local'},
            {'label': 'Polar', 'value': 'polar'},
        ],
        value = "local"
    ),
    html.Div(id='choice-display-value',children=''),
])

#Callback for data_dropdown which changes page layout depending on dropdown value
#Writes new layout in choice-display-value children
@app.callback(
    Output('choice-display-value', 'children'),
    Input('data_dropdown', 'value'))
def display_value(value):
    print(value)
    #load localdata layout
    if (value == 'local'):
        print(value)
        return localdata.layout
    
    #load polar layout
    if (value == 'polar'):
        #Insert Polar integration here
        

        config = load_config(CONFIG_FILENAME)
        if config == None:
            return PreventUpdate

        if 'refresh_token' in config.keys() and config["refresh_token"] != "" and ('access_token' not in config.keys() or config["access_token"] == None):
            access_token = requests.post(f"https://auth.polar.com/oauth/token?refresh_token={ config['refresh_token'] }&grant_type=refresh_token", auth=HTTPBasicAuth(config['client_id'], config['client_secret'])).json()['access_token']
            config['access_token'] = access_token
            save_config(config, "config.yml")
            return dcc.Location(href="/pages/data_choice", id="someid_doesnt_matter")

        index = accesslink.authorization_url.find('redirect_uri')
        neuer_link = str(accesslink.authorization_url)[0:index]
        neuer_link = neuer_link + 'scope=team_read'

        return dcc.Location(href=neuer_link, id="someid_doesnt_matter")
    
