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

layout = html.Div(id='zonelayout',children=[
    html.H1("Zones:"),
    dcc.RadioItems(
        id="zone_radio",
        options=[
            {'label': 'Speedzones', 'value': 'speed'},
            {'label': 'heartratezones', 'value': 'heartrate'}
        ],
        #value='speed',
    ),
    html.Div(id="zone_graph",children=[])
])

@app.callback(
    Output('zone_graph','children'),
    Input('zone_radio','value')
)
def choose_zone(choosen_zone):
    if choosen_zone == 'speed':
            speedlayout = [html.Div([
            html.H1("Speedzones:"),
            html.Label("Seperate speedzones by ',':"),
            html.Br(),
            dcc.Input(id="speedzone-input", value="0,5,15,20,30"),
            dcc.Graph(
                id='speedzones-graph',
                config= {'displayModeBar': False, 'scrollZoom': False, },
                #layout = go.Layout(template='plotly_dark')
            ),
            html.Button('Generate', id='gen_speedzones', n_clicks=0)])]
            return speedlayout
    if choosen_zone == 'heartrate':
            heartlayout = [html.Div([
            html.H1("Heartratezones:"),
            html.Label("Seperate Heartratezones by ',':"),
            html.Br(),
            dcc.Input(id="heartratezone-input", value="0,5,15,20,30"),
            dcc.Graph(
                id='heartratezones-graph',
                config= {'displayModeBar': False, 'scrollZoom': False, },
                #layout = go.Layout(template='plotly_dark')
            ),
            html.Button('Generate', id='gen_heartratezones', n_clicks=0)])]
            return heartlayout
    else:
        raise PreventUpdate

#Insert heartratecallback here
"""
@app.callback(
    Output("heartratezones-graph", "figure"),
    Input("gen_heartratezones", "n_clicks"),
    State("heartratezone-input", "value"))
def update_heartratezone_figure(n_clicks, heartzone_input):
    df = am.df
    print(df.keys())
    heartzones = []
    temp_heartzones = heartzone_input.split(',')
    for zone in temp_heartzones:
        heartzones.append(float(zone.strip()))
    return 'lul' """


@ app.callback(
    Output("speedzones-graph", "figure"),
    Input("gen_speedzones", "n_clicks"),
    State("speedzone-input", "value"))
def update_speedzone_figure(n_clicks, speedzone_input):
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