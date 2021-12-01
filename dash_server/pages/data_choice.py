from threading import local
import dash as ds
from dash import dependencies
from dash import html
from dash import dcc
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import utils

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
        

        config = utils.load_config(utils.CONFIG_FILENAME)
        if config == None:
            return PreventUpdate

        if 'refresh_token' in config.keys() and config["refresh_token"] != "" and ('access_token' not in config.keys() or config["access_token"] == None):
            utils.accesslink.get_access_token()
            return dcc.Location(href="/pages/data_choice", id="someid_doesnt_matter")

        index = utils.accesslink.authorization_url.find('redirect_uri')
        neuer_link = str(utils.accesslink.authorization_url)[0:index]
        neuer_link = neuer_link + 'scope=team_read'

        return dcc.Location(href=neuer_link, id="someid_doesnt_matter")
    
