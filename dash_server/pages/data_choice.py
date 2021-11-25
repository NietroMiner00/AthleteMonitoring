from threading import local
import dash as ds
from dash import dependencies
from dash import html
from dash import dcc
from dash.dependencies import Input, Output, State

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
        return 'Polar not integrated yet'
    
