from inspect import Parameter
from multiprocessing.sharedctypes import Value
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

layout = html.Div(id='zonelayout', children=[
    html.H1("Zones:"),
    dcc.RadioItems(
        id="zone_radio",
        options=[
            {'label': 'Speedzones', 'value': 'speed'},
            {'label': 'heartratezones', 'value': 'heartrate'}
        ],
        value='speed'
    ),
    html.Div(id="zone_graph", children=[
        html.Div([
                html.H3("Relativ Percentage or Total time spend in Minutes?"),
                dcc.RadioItems(
                    id='relortot',
                    options=[
                        {'label': 'Relativ', 'value': 'rel'},
                        {'label': 'Total', 'value': 'tot'}
                    ],
                    value='rel'
                ),
            html.Label("Seperate zones by ',':"),
            html.Br(),
            dcc.Input(id="speedzone-input", value="0,5,15,20,30", debounce=True),
            dcc.Loading(
                    id="loading-1",
                    type="default",
                    children=[
                        dcc.Graph(
                            id='speedzones-graph',
                            config={'displayModeBar': False},

                        )
                    ]
                    )
        ]),
        #Store component for all players currently visible in the graphs legend
        dcc.Store(
            id="visible-players",
            data=[]
        )
    ])
])

#Callback for the Zones (Currently: Speedzones/Heartratezones)
@ app.callback(
    Output("speedzones-graph", "figure"),
    Output('visible-players', 'data'),
    Input("zone_radio", "value"),
    Input('example-graph', 'restyleData'),
    Input('example-graph', 'figure'),
    Input("speedzone-input", "value"),
    Input('relortot', 'value'),
    State('visible-players', 'data'),
    State('recording_times','data')
)
def update_speedzone_figure(zone_type, speed_graph, speed_graph_fig, speedzone_input, relativortotal,visible_players, recording_times):
    df = am.df

    #Prevent Update is neccesary keys not in dataframe
    if "speed" not in df :
        raise PreventUpdate
    if "hr" not in df:
        raise PreventUpdate
    
    #Get manualy entered zones
    zones = []
    try:
        temp_speedzones = speedzone_input.split(',')
        for zone in temp_speedzones:
            zones.append(float(zone.strip()))
    except Exception: # Bad practice
        raise PreventUpdate

    teams = df['playerID'].drop_duplicates().values

    #Check RadioItem wether speedzones or heartzones are selected
    #determins different total and variable for further processing
    speedzones = []
    if(zone_type == 'speed'):
        total = df.groupby('playerID').speed.count()
        zone_type_dt = 'speed'
    else:
        total = df.groupby('playerID').hr.count()
        zone_type_dt = 'hr'

    #Repeat for every zone
    for index, zone in enumerate(zones):
        #Are we on the last element yet?
        #No
        if index < len(zones)-1:
            #Is the RadioItem set to relativ or total?
            #Relativ
            if(relativortotal == 'rel'):
                #Append a dataframe with all entires where the current entry is greater than the current zone and lower than the next zone
                #Sort these by playerID and get the count of all entries, divide them by the total to get percentages
                speedzones.append(
                    df[
                        (df[zone_type_dt] >= zones[index]) & (df[zone_type_dt] < zones[index+1])
                    ].groupby('playerID')[zone_type_dt]
                    .count() / total)
            #Total
            if(relativortotal == 'tot'):
                #Same as relativ above but sorted count is divied by 60 to display minutes(One entry roughly equates to one second)
                temp_df = df[
                    (df[zone_type_dt] >= zones[index]) & (df[zone_type_dt] < zones[index+1])
                ].groupby('playerID')[zone_type_dt].count()

                temp_df = temp_df / 60
                
                speedzones.append(temp_df)
        #Yes
        else:
            if(relativortotal == 'rel'):
                #Same as above but checks whether current entry is less than infinit
                speedzones.append(
                    df[
                        (df[zone_type_dt] >= zones[index]) & (df[zone_type_dt] < np.inf)
                    ].groupby('playerID')[zone_type_dt]
                    .count() / total
                )

            #Only works for Speedzones and not for Heartratezones god know why.....
            if(relativortotal == 'tot'):
                speedzones.append(
                    df[
                        (df[zone_type_dt] >= zones[index]) & (df[zone_type_dt] < np.inf)
                    ].groupby('playerID')[zone_type_dt]
                    .count() / 60
                )


    # detect visible players in 'example-graph'
    speedzones_df = pd.DataFrame([speedzone.array for speedzone in speedzones], columns=teams)
    
    for i in range(len(visible_players), len(teams)):
        visible_players.append(True)

    if speed_graph is not None:
        edits, indices = speed_graph
        try:
            for visible, index in zip(edits["visible"], indices):
                is_visibale = visible != 'legend_only' and visible is True
                visible_players[index] = is_visibale
        except KeyError:
            pass

    players = teams[visible_players]
    fig = px.bar(speedzones_df)

    # 2 columns for 2 or less selected players and 3 columns for more
    fig = make_subplots(rows=int(np.ceil(len(players)/3)),
                        cols=2 if len(players) < 3 else 3, subplot_titles=players)

    for index, player in enumerate(players):
        fig.add_trace(go.Bar(x=speedzones_df[player], y=speedzones_df.index + 1, marker_color=speedzones_df.index,
                      orientation="h"), row=int(np.ceil((index+1)/3)), col=(index) % 3 + 1)

    #Update plot axes and layout for styling purposes
    fig.update_xaxes(
        showgrid=False,
        showline=False,
        showticklabels=False,
        fixedrange=True
    )

    fig.update_yaxes(
        showgrid=False,
        showline=False,
        dtick=1,
        fixedrange=True
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
