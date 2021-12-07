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
            teams = utils.api.get_teams()
            if type(teams) == dcc.Location:
                return teams # Redirect if no refresh_token
            return html.Div([dcc.Dropdown(id='polar-drop',options=[{'label': team['name'],'value': team['id']} for team in teams]), html.Div(id="sessions")],id='drop_div')
        else:
            return logged_in[1]

@app.callback(
    Output('sessions', 'children'),
    Input('polar-drop', 'value'))
def show_team_details(team):
    print(team)
    if team == None:
        raise PreventUpdate
    sessions = utils.api.get_sessions(team)
    session_collection= []
    for amount, session in enumerate(sessions):
        date = session['created']
        starttime = session['start_time']
        endtime = session['end_time']
        new_session= html.Div([
            html.H5(f'Session: {amount}'),
            html.P(f'Datum: {date}, Starttime: {starttime}, Endtime: {endtime}'),
            html.Button('Download', id=f'button_load_session{amount}', n_clicks=0)
        ])
        session_collection.append(new_session)
    return session_collection