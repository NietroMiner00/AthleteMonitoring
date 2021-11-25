import dash as ds
from dash import dependencies
import plotly.express as px
import pandas as pd
import Data_processing as pp
from dash import html 
from dash import dcc

from app import app

#Assigns processed sports data to dataframe
df = pp.process_data()

#draws first graph which will be displayed on load 
#only temporary until some kind of main menu exists
fig = px.scatter(df, x="Time", y="v", color="playerID")

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
                            {'label': 'Line', 'value': 'lin'},
                            {'label': 'Scatter', 'value': 'sca'},
                            {'label': 'Bar', 'value': 'bar'}
                        ],
                        value='sca'
                    ),
                    html.Div(id='gs_output_container'),
                ]),
                html.Div(
                    html.Button('Generate', id='gen_graph', n_clicks=0)),
                ]),
    #draws Graphs
    dcc.Graph(
        id='example-graph',
        figure=fig
    )
])

#Callback to dynamically change figure based on current selected dropdown option via button input.
@ app.callback(
    dependencies.Output(component_id="example-graph",
                        component_property="figure"),
    [dependencies.Input(component_id="gen_graph",
                        component_property="n_clicks")],
    [dependencies.State(component_id='graphstyle',
                        component_property="value")],
    prevent_initial_call=True)

#returns new figure depending on current state of the dropdown value
#n_clicks is a stand in for button clicked/ current_state is taken from the current value of the dropdown menu "graphstyle"
#update_figure is called on buttonpress, that may be obsolet but i did not find a way to stop it from triggering on every callback yet
def update_figure(n_clicks, current_state):
    if(current_state == "lin"):
        #Linegraph
        fig = px.line(df, x="Time", y="v", color="playerID")
        return fig
    if(current_state == "sca"):
        #Scattergraph
        fig = px.scatter(df, x="Time", y="v", color="playerID")
        return fig
    if(current_state == "bar"):
        #Bargraph
        fig = px.bar(df, x="Time", y="v", color="playerID")
        return fig
    raise ds.exceptions.PreventUpdate


"""if __name__ == '__main__':
    #Whilst debug allows for addtional options during execution it also runs the whole program twice on load
    app.run_server(debug=False)"""
