from threading import local
import dash as ds
from dash import dependencies,html,dcc,callback_context
from dash.dependencies import Input, Output, State, ALL
from dash.exceptions import PreventUpdate
import utils
import requests
import os
from datetime import datetime
import numpy as npy

from app import app
from pages import localdata
queue = []

layout = html.Div(children=[
    html.Div(id="header_data_choice",children=[
        html.H1("Athlete Monitoring APP")

    ]),
    html.Div(id="data_selection_first_page",children=[
        html.H2('Do you already have data available?: '),
        # Dropdown with either Local or Polar option
        dcc.Dropdown(
            id='data_dropdown',
            options=[
                {'label': 'Yes, local .csv/.xls/... files', 'value': 'local'},
                {'label': 'No, i need to access Polar', 'value': 'polar'},
            ],
            
        ),
        html.Div(
            id='choice-display-value', children='')])
])

# Callback for data_dropdown which changes page layout depending on dropdown value
# Writes new layout in the children component of the div choice-display-value
@app.callback(
    Output('choice-display-value', 'children'),
    Input('data_dropdown', 'value'))
def display_value(value):
    # load localdata layout
    if (value == 'local'):
        return localdata.layout

    # load polar layout
    if (value == 'polar'):
        logged_in = utils.accesslink.logged_in()
        if logged_in[0]:
            # Fetch team and return dropdown with chooseable team
            teams = utils.api.get_teams()
            if type(teams) == dcc.Location:
                return teams  # Redirect if no refresh_token
            return html.Div(children=[html.H3("Please select your team:"),dcc.Dropdown(id='polar-drop', options=[{'label': team['name'], 'value': team['id']} for team in teams]), html.Div(id="sessions"), html.Div(id="downqueue")], id='drop_div')
        else:
            return logged_in[1]

# callback for displaying sessions of, in "polar-drop", choosen team
@app.callback(
    Output('sessions', 'children'),
    Input('polar-drop', 'value'))
def show_team_details(team):
    if team == None:
        raise PreventUpdate

    # fetch all sessions for given team
    sessions = utils.api.get_sessions(team)

    # array of new divs we want to add
    session_collection = []
    session_head= html.Div(id="session_header",children=[html.H3("The following sessions are available:")])
    session_collection.append(session_head)
    # iterates over all available sessions
    for amount, session in enumerate(sessions):
        # gets date,start-and endtime from current session
        date = session['created']
        starttime = session['start_time']
        endtime = session['end_time']

        # creates new div with title, date, starttime, endtime and a download button
        new_session = html.Div(id="session_div",children=[
            html.H4(f'Session: {amount}'),
            html.P(f'Datum: {date}'),
            html.P(f'Starttime: {starttime}'), 
            html.P(f'Endtime: {endtime}'),
            html.Button('Add to Queue', id={
                        'type': 'button_load_session', 'index': amount}, n_clicks=0)
        ])
        # appends new div to session_collection
        session_collection.append(new_session)

    #Divs for downloadqueue and buttons
    session_list = html.Div(className="queue",children=[html.Div([html.Ul(id="downqueue",children=[html.Li(i) for i in queue]),
            html.Br(),
            html.Button('Download Queue', id="downloadqueue", n_clicks=0), 
            html.Button('Add All', id="addall", n_clicks=0),
            html.Button('Empty Queue', id="emptyqueue", n_clicks=0)])])

    session_collection.append(session_list)
    return session_collection  # returns collection of divs to append to layout

#Callback for Queue (Add singel, add multiple, clear list)
@app.callback(Output('downqueue', 'children'),
              Input({'type': 'button_load_session', 'index': ALL}, 'n_clicks'),
              Input('addall', 'n_clicks'),
              Input('emptyqueue','n_clicks'),
              State('polar-drop', 'value'))
def addtodownload(n_clicks_single,n_clicks_all,n_clicks_empty, team_id):
    #Get id of item which changed state since last call
    changed_id = [p['prop_id'] for p in callback_context.triggered][0]

    #Add all has been presses
    #return list with all sessions
    if 'addall' in changed_id :
        queue.clear()
        sessions = utils.api.get_sessions(team_id)
        for i, session in enumerate(sessions):
            session_id = session['id']
            queue.append(session_id)
        return html.Div([html.Ul(children=[html.Li(i) for i in queue])])

    #empty queue
    #return empty list
    if 'emptyqueue' in changed_id:
        queue.clear()
        return html.Div([html.Ul(children=[])])

    #Checks wether one of the single downloadbuttons has been pressed
    # if pressed add corresponding session to queue 
    for i in range(len(n_clicks_single)):
        if f'"index":{i},"type":"button_load_session"' in changed_id:
            sessions = utils.api.get_sessions(team_id)
            session = sessions[i]
            session_id = session['id']
            for i,idinqueue in enumerate(queue):
                if session_id == idinqueue:
                    return html.Div([html.Ul(children=[html.Li(i) for i in queue])])
            queue.append(session_id)
            return html.Div([html.Ul(children=[html.Li(i) for i in queue])])

# Callback to download sessions in "queue" when "Download Queue button has been pressed"
@app.callback(
    Output('downloadqueue', "n_clicks"),
    Input('downloadqueue', "n_clicks"),
    State('polar-drop', 'value'))
def downloadqueue_callback(n_clicks, team_id):
    if n_clicks == 0:
        raise PreventUpdate
    print("Starte Download")
    teams = utils.api.get_teams()
    team_name = None
    for team in teams:
        if team['id'] == team_id:
            team_name = team['name']
            if team_name == None:
                raise Exception("Something went horribly wrong!!!")

    #Only for internal time comparison
    # remove before end of project
    totaltime = []
    totaldownloadstart = datetime.now()
    ##
    ##
    
    for i, session_id in enumerate(queue):
        print(f"Downloade Nr.{i} mit ID {session_id}")

        ###
        # Only for internal comparison of downloadtime
        # remove before end of project
        timemeasure = datetime.now()
        starttime = timemeasure
        print(f"Time{starttime}")
        ###

        participants_data = utils.api.get_participants_data(session_id)
        start_time, end_time = utils.api.get_timestamps(session_id)
        start_time = start_time.replace(':', '-')
        end_time = end_time.replace(':', '-')
        session_path = f"data/{team_name}"
        if not os.path.exists(session_path):
            os.makedirs(session_path)
        participants_data.to_parquet(session_path + f"/{start_time} {end_time} {session_id}.parquet")
        

        ###
        # Only for internal comparison of downloadtime
        # remove before end of project
        timemeasure = datetime.now()
        endtime = timemeasure
        print(f"Time{endtime} ")
        currenttotaltime = endtime - starttime
        totaltime.append(((endtime - starttime).total_seconds())/60)
        print(f'Total Time for this querey: {currenttotaltime}')
        ###
        ###


        print(f"{i} Abgeschlossen")
    
    ##
    ###
    # Only for internal comparison of downloadtime
    # remove before end of project
    totaldownloadend = datetime.now()
    insgesamtzeit = (totaldownloadend-totaldownloadstart)
    totalmax= npy.amax(totaltime)*60
    totalmin = npy.amin(totaltime)*60
    totalave = npy.average(totaltime)*60
    print(f"Insgesamte Downloadzeit: {insgesamtzeit}")
    print(f'Maximale Downloadzeit: {totalmax}')
    print(f'Minimalste Downloadzeit: {totalmin}')
    print(f'Total Average: {totalave}')
    ###
    ###