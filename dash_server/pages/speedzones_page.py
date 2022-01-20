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
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from app import app

layout = html.Div([
    html.H1("Speedzones:"),
    html.Label("Seperate speedzones by ',':"),
    html.Br(),
    dcc.Input(id="speedzone-input", value="0,5,15,20,30"),
    dcc.Graph(
        id='speedzones-graph',
        config= {'displayModeBar': False, 'scrollZoom': False, },
        #layout = go.Layout(template='plotly_dark')
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

    speedzones_df = pd.DataFrame([speedzone.array for speedzone in speedzones], columns=speedzones[0].index.array)

    fig = px.bar(speedzones_df)

    fig = make_subplots(rows=2)

    fig.add_trace(go.Bar(x=speedzones_df['BO5e35el'], y=speedzones_df.index + 1, marker_color=speedzones_df.index, orientation="h"), row=1, col=1)

    fig.update_layout(template="plotly_dark",
        xaxis=dict(
            showgrid=False,
            showline=False,
            showticklabels=False,
            fixedrange = True
        ),
        yaxis=dict(
            showgrid=False,
            showline=False,
            dtick=1,
            fixedrange = True
        ),
        margin=dict(
            b=0,
            t=0,
            l=0,
            r=0
        ),
        bargap=0
    )
    return fig