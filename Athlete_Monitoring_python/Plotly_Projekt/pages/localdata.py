import dash as ds
from dash.exceptions import PreventUpdate
from dash import html
from dash import dcc
from dash.dependencies import Input, Output, State
import glob
import pandas as pd

from app import app

layout = html.Div([
    html.Div([
        html.H2('Data needs to be stored in: Athlete_Monitoring_python\Plotly_Projekt\Data'),
        dcc.Textarea(
            id='data_area',
            value='',
            style={'width':'100%', 'height':300},
            readOnly=True
        ),
        html.Button('Read Data', id='data_read', n_clicks=0),
    ]),
     html.Div(id='data_display', children='')

])


@app.callback(Output('data_area','value'),
            Input('data_read','n_clicks'))
def data_display(n_clicks):
    if n_clicks is None:
        raise PreventUpdate
    files_parq = glob.glob('Data/*.parquet')
    files_csv = glob.glob("Data/*.csv")
    files_xls = glob.glob("Data/*.xls")
    files_feather = glob.glob('Data/*.fea')
    files_npy = glob.glob("Data/*.npy")
    files_json = glob.glob("Data/*.json")
    return f'Currently available:\n Excel: {files_xls}\n JSON: {files_json}\n Numpy: {files_npy}\n Parquet: {files_parq}'
    
@app.callback(Output('data_display','children'),
            Input('data_read','n_clicks'),
            State('data_display', 'children'))
def add_link(n_clicks,children):
    if n_clicks is None:
        raise PreventUpdate
    return html.Div(dcc.Link('Proceed', href='/apps/Athlete_Monitoring'))

"""
@app.callback(Output('data_display', 'children'),
              Input('data_read', 'n_clicks'))
def display_data(n_clicks):
    
    for i,csv in enumerate(files_csv):
        files_csv[i] = pd.read_csv(csv) 

    for i,xls in enumerate(files_xls):
        files_xls[i] = pd.read_excel(xls)
        print(files_xls)

    for i,fea in enumerate(files_feather):
        files_feather[i] = pd.read_feather(fea)"""

    
