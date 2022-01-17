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
    dcc.Graph(
        id='speedzones-graph'
    ),
    html.Button('Generate', id='gen_speedzones', n_clicks=0),
])

@ app.callback(
    Output("speedzones-graph", "figure"),
    Input("gen_speedzones", "n_clicks"))
def update_figure(n_clicks):
    df = am.df

    zones = [5, 12, 20, 25, 30]
    if "speed" not in df:
        raise PreventUpdate

    total = df.groupby('playerID').speed.count()
    speedzone1 = df[(df['speed'] >= 0) & (df['speed'] < zones[0])].groupby('playerID').speed.count() / total
    speedzone2 = df[(df['speed'] >= zones[0]) & (df['speed'] < zones[1])].groupby('playerID').speed.count() / total
    speedzone3 = df[(df['speed'] >= zones[1]) & (df['speed'] < zones[2])].groupby('playerID').speed.count() / total
    speedzone4 = df[(df['speed'] >= zones[2]) & (df['speed'] < zones[3])].groupby('playerID').speed.count() / total
    speedzone5 = df[(df['speed'] >= zones[3]) & (df['speed'] < zones[4])].groupby('playerID').speed.count() / total
    speedzone6 = df[(df['speed'] >= zones[4]) & (df['speed'] < np.inf)].groupby('playerID').speed.count() / total

    speedzones = pd.DataFrame([speedzone1.array, speedzone2.array, speedzone3.array, speedzone4.array, speedzone5.array, speedzone6.array, ], columns=speedzone1.index.array)
    print(speedzones)
    fig = px.bar(speedzones)
    return fig