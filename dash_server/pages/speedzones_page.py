from inspect import Parameter
import time
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
    html.Div(id="zone_graph",children=[
        html.Div([
            html.H1("Speedzones:"),
            html.Label("Seperate speedzones by ',':"),
            html.Br(),
            dcc.Input(id="speedzone-input", value="0,5,15,20,30"),
            dcc.Loading(
                id="loading-1",
                type="default",
                children=[
                    dcc.Graph(
                        id='speedzones-graph',
                        config= {'displayModeBar': False},
                        #layout = go.Layout(template='plotly_dark')
                    )
                ]
            )
        ])
    ]),
    dcc.Store(
        id="visible-players",
        data=[]
    )
])


def choose_zone(choosen_zone):
    if choosen_zone == 'speed':
            speedlayout = [
                
            ]
            return speedlayout
    if choosen_zone == 'heartrate':
            heartlayout = [html.Div([
            html.H1("Heartratezones:"),
            html.Label("Seperate Heartratezones by ',':"),
            html.Br(),
            dcc.Input(id="heartratezone-input", value="0,5,15,20,30"),
            dcc.Graph(
                id='heartratezones-graph',
                config= {'displayModeBar': False},
                #layout = go.Layout(template='plotly_dark')
            )])]
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
    Output('visible-players', 'data'),
    Input("zone_radio", "value"),
    Input('example-graph', 'restyleData'),
    State("speedzone-input", "value"),
    State('visible-players', 'data'))
def update_speedzone_figure(zone_type, speed_graph, speedzone_input, visible_players):
    df = am.df
    print("draw speedzones")

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

    print(speed_graph)

    for i in range(len(visible_players), len(speedzones[0].index.array)):
        visible_players.append(True)

    # detect visible players in 'example-graph'
    if speed_graph is not None:
        edits, indices = speed_graph
        try:
            for visible, index in zip(edits["visible"], indices):
                # visible could be the string "legend_only" which is truthy
                # hence explicit comparison to True here
                is_visibale = visible != 'legend_only' and visible is True
                
                visible_players[index] = is_visibale
        except KeyError:
            pass

    print(visible_players)

    players = speedzones[0].index.array[visible_players]

    print(players)
    print(int(len(players)/3))

    fig = px.bar(speedzones_df)

    fig = make_subplots(rows=int(np.ceil(len(players)/3)), cols=3, subplot_titles=players)

    for index, player in enumerate(players):
        print((index) % 3 + 1, int(np.ceil((index+1)/3)))
        fig.add_trace(go.Bar(x=speedzones_df[player], y=speedzones_df.index + 1, marker_color=speedzones_df.index, orientation="h"), row=int(np.ceil((index+1)/3)), col=(index) % 3 + 1)

    fig.update_xaxes(
        showgrid=False,
        showline=False,
        showticklabels=False,
        fixedrange = True
    )

    fig.update_yaxes(
        showgrid=False,
        showline=False,
        dtick=1,
        fixedrange = True
    )

    fig.update_layout(template="plotly_dark",
        margin=dict(
            b=0,
            t=50,
            l=0,
            r=0
        ),
        bargap=0,
        showlegend=False
    )
    return fig, visible_players