from inspect import Parameter
from re import template
import dash as ds
from dash.dependencies import Output, Input, State
from pandas.core.frame import DataFrame
import plotly.express as px
import pandas as pd
import Data_processing as pp
from dash import html 
from dash import dcc
from urllib import parse
import pages.speedzones_page as sp
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from app import app

df = DataFrame()

#Layout construction similar to html syntax
#Current layout is neither optimised nor especially beautiful so feel free to adjust divs  
layout = html.Div(children=[
    html.H1(children='Athlete Monitoring: Example'),
    html.Div([
                html.Div([
                    dcc.Dropdown(
                        id='graphstyle',
                        options=[
                            {'label': 'All Player Speed x Time', 'value': 'lin'},
                            {'label': 'One Player Speed x Time + HR', 'value': 'sca'}
                        ],
                        value='lin'
                    ),
                    html.Div(id='gs_output_container'),
                ]),
                html.Div(
                    html.Button('Generate', id='gen_graph', n_clicks=0)),
                ]),
    #draws Graphs
    dcc.Loading(
        id="loading-1",
        type="default",
        children=[
            dcc.Graph(
                id='example-graph',
                config= {'displayModeBar': False},
                #layout = go.Layout(template='plotly_dark')
            )
        ]
    ),
    sp.layout,
    dcc.Store(
        id='recording_times',
        data=[]
    )
])

#Callback to dynamically change figure based on current selected dropdown option via button input.
@ app.callback(
    Output("example-graph", "figure"),
    Output('recording_times','data'),
    Input("gen_graph", "n_clicks"),
    State('graphstyle', "value"),
    State("url", "href"),
    State('recording_times','data'))

#returns new figure depending on current state of the dropdown value
#n_clicks is a stand in for button clicked/ current_state is taken from the current value of the dropdown menu "graphstyle"
#update_figure is called on buttonpress, that may be obsolet but i did not find a way to stop it from triggering on every callback yet
def update_figure(n_clicks, current_state, href,recording_times):
    global df
    df = DataFrame()
    print("draw not speedzones")

    query = parse.urlparse(href).query
    parameters = parse.parse_qs(query)

    df = pp.process_data(parameters['file'][0])

    file_params = parameters['file'][0].replace('\\', '/').split('/')[-1].split(' ') # start_time, end_time, (session_id + .parquet)
    file_params[0] = f"{file_params[0].split('T')[0]} {file_params[0].split('T')[1].replace('-', ':')}"
    file_params[1] = f"{file_params[1].split('T')[0]} {file_params[1].split('T')[1].replace('-', ':')}"
    
    recording_times = file_params



    if(current_state == "lin"):

        fig = px.line(df, x="Time", y="speed", color="playerID",
            title="Speed in relation to time",
            labels={"Time": "Session Time" , "speed" : "Achived Speed", "playerID": "Player"},
            template="plotly_dark"
        )
        
        # Add vertical start and end time lines
        start_time, end_time = pd.to_datetime(recording_times[0:2])
        
        fig.add_vline(x=start_time,line_color='white',line_dash="dash")
        fig.add_vline(x=end_time,line_color='white',line_dash="dash")

        return fig, recording_times

    if(current_state == "sca"):
        #fig = px.line(df, x="Time", y="v", color="playerID")

        fig = make_subplots(specs=[[{"secondary_y": True}]])

        # Add traces
        fig.add_trace(
            go.Scatter(x=df['Time'][df['playerID'] == "BO5e35el"], y=df['speed'][df['playerID'] == "BO5e35el"], name="Speed"),
            secondary_y=False,
        )

        fig.add_trace(
            go.Scatter(x=df['Time'][df['playerID'] == "BO5e35el"], y=df['hr'][df['playerID'] == "BO5e35el"], name="Heart Rate"),
            secondary_y=True,
        )

        # Add vertical start and end time lines
        start_time, end_time = pd.to_datetime(recording_times[0:2])
        
        fig.add_vline(x=start_time,line_color='white',line_dash="dash")
        fig.add_vline(x=end_time,line_color='white',line_dash="dash")

        # Set x-axis title
        fig.update_xaxes(title_text="Session Time")

        # Set y-axes titles
        fig.update_yaxes(
            title_text="<b>Achieved</b> Speed",
            secondary_y=False)
        fig.update_yaxes(
            title_text="<b>Current</b> Heart Rate", 
            secondary_y=True)

        fig.update_layout(template="plotly_dark")

        

        return fig,recording_times

    raise ds.exceptions.PreventUpdate