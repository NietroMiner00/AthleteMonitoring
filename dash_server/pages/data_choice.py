from threading import local
import dash as ds
from dash import dependencies
from dash import html
from dash import dcc
from dash.dependencies import Input, Output, State, ALL
from dash.exceptions import PreventUpdate
import utils
import requests
import os

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
            html.Button('Download', id={'type':'button_load_session', 'index':amount}, n_clicks=0)
        ])
        session_collection.append(new_session)

    return session_collection

@app.callback(
    Output({'type':'button_load_session', 'index':ALL}, "n_clicks"),
    Input({'type':'button_load_session', 'index':ALL}, 'n_clicks'),
    State('polar-drop', 'value')
)
def on_load_session(n_clicks, team_id):
    for i in range(len(n_clicks)):
        if n_clicks[i]:
            teams = utils.api.get_teams()

            team_name = None
            for team in teams:
                if team['id'] == team_id:
                    team_name = team['name']
            if team_name == None:
                raise Exception("Something went horribly wrong!!!")

            sessions = utils.api.get_sessions(team_id)
            session = sessions[i]
            session_id = session['id']

            participants_data = utils.api.get_participants_data(session_id)

            session_path = f"data\{team_name}"
            if not os.path.exists(session_path):
                os.mkdir(session_path)
            participants_data.to_parquet(session_path + f"\{session['start_time'].replace(':', '-')}-{session_id}.parquet")

            break
        n_clicks[i] = 0
    return n_clicks