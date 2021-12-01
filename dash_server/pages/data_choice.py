from threading import local
import dash as ds
from dash import dependencies
from dash import html
from dash import dcc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import utils
import requests

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
    html.Div(
        id='choice-display-value', children='')
    ])

#Callback for data_dropdown which changes page layout depending on dropdown value
#Writes new layout in choice-display-value children
@app.callback(
    Output('choice-display-value', 'children'),
    Input('data_dropdown', 'value'))
def display_value(value):
    #load localdata layout
    if (value == 'local'):
        return localdata.layout
    
    #load polar layout
    if (value == 'polar'):
        logged_in = utils.accesslink.logged_in()
        if logged_in[0]:
            #Fetch team and return dropdown with chooseable team
            config = utils.load_config("config.yml")
            headers = {
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + config['access_token']}
            teams = requests.get('https://teampro.api.polar.com/v1/teams/', params={}, headers=headers).json()['data']
            return html.Div([dcc.Dropdown(id='polar-drop',options=[{'label': team.get('name'),'value': team.get('id')} for team in teams])])
        else:
            return logged_in[1]