from inspect import Parameter
import dash as ds
from dash.dependencies import Output, Input, State
from dash.exceptions import PreventUpdate
from pandas.core.frame import DataFrame
import plotly.express as px
import pandas as pd
import numpy as np
import Data_processing as pp
from dash import html 
from dash import dcc
from urllib import parse
import pages.Athlete_Monitoring as am

from app import app

layout = html.Div([
    html.H1("Speedzones:"),
    html.Label("Seperate speedzones by ',':"),
    html.Br(),
    dcc.Input(id="speedzone-input", value="0,5,15,20,30"),
    dcc.Graph(
        id='speedzones-graph'
    ),
    html.Button('Generate', id='gen_speedzones', n_clicks=0),
])

@ app.callback(
    Output("speedzones-graph", "figure"),
    Input("gen_speedzones", "n_clicks"),
    State("speedzone-input", "value"))
def update_figure(n_clicks, speedzone_input):
    df = am.df

    zones = []
    temp_speedzones = speedzone_input.split(',')
    for zone in temp_speedzones:
        zones.append(float(zone.strip()))

    if "speed" not in df:
        raise PreventUpdate

    total = df.groupby('playerID').speed.count()
    speedzones = []
    for index, zone  in enumerate(zones):
        if index < len(zones)-1:
            speedzones.append(
                df[
                    (df['speed'] >= zones[index]) & (df['speed'] < zones[index+1])
                ].groupby('playerID')
                .speed
                .count() / total
            )
        else:
            speedzones.append(
                df[
                    (df['speed'] >= zones[index]) & (df['speed'] < np.inf)
                ].groupby('playerID')
                .speed
                .count() / total
            )

    speedzones = pd.DataFrame([speedzone.array for speedzone in speedzones], columns=speedzones[0].index.array)
    fig = px.bar(speedzones)
    return fig