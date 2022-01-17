from inspect import Parameter
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

from app import app

df = DataFrame()

#Layout construction similar to html syntax
#Current layout is neither optimised nor especially beautiful so feel free to adjust divs  
layout = html.Div(children=[
    html.H1(children='Athlete Monitoring: Example',
               style={'textAlign': 'center'},),
    html.Div([
                html.Div([
                    dcc.Dropdown(
                        id='graphstyle',
                        options=[
                            {'label': 'Data from API', 'value': 'lin'},
                            {'label': 'Data from GPS', 'value': 'sca'}
                        ],
                        value='lin'
                    ),
                    html.Div(id='gs_output_container'),
                ]),
                html.Div(
                    html.Button('Generate', id='gen_graph', n_clicks=0)),
                ]),
    #draws Graphs
    dcc.Graph(
        id='example-graph'
    ),
    sp.layout
])

#Callback to dynamically change figure based on current selected dropdown option via button input.
@ app.callback(
    Output("example-graph", "figure"),
    Input("gen_graph", "n_clicks"),
    State('graphstyle', "value"),
    State("url", "href"))

#returns new figure depending on current state of the dropdown value
#n_clicks is a stand in for button clicked/ current_state is taken from the current value of the dropdown menu "graphstyle"
#update_figure is called on buttonpress, that may be obsolet but i did not find a way to stop it from triggering on every callback yet
def update_figure(n_clicks, current_state, href):
    global df
    df = DataFrame()

    query = parse.urlparse(href).query
    parameters = parse.parse_qs(query)

    df = pp.process_data(parameters['file'][0])

    if(current_state == "lin"):
        #Linegraph
        fig = px.line(df, x="Time", y="speed", color="playerID",
        title="Speed in relation to time",
        labels={"Time": "Session Time" , "speed" : "Achived Speed", "playerID": "Player"},
        template="plotly_dark")
        return fig
    if(current_state == "sca"):
        #Scattergraph
        fig = px.line(df, x="Time", y="v", color="playerID")
        return fig
    raise ds.exceptions.PreventUpdate