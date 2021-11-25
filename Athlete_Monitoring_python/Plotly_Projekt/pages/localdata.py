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
        dcc.Dropdown(
            id='local_dropdown'
        ),
    ]),
     html.Div(id='data_display', children=''),
     html.Div(id="hidden_div_for_redirect_callback")
])


@app.callback(Output('local_dropdown','options'),
            Input('data_dropdown','value'))
def data_display(value):
    if value == "local":
        types = ("Data/*.parquet", "Data/*.csv", "Data/*.xls", "Data/*.fea", "Data/*.npy", "Data/*.json")
        files_grabbed = []
        for files in types:
            files_grabbed.extend(glob.glob(files))
        return [{"label": file.replace("Data\\", ""), "value": file} for file in files_grabbed]
    raise PreventUpdate

@app.callback(Output("hidden_div_for_redirect_callback", "children"),
                Input("local_dropdown", "value"))
def read_selected_file(value):
    if value == None:
        raise PreventUpdate
    return dcc.Location(href=f"/pages/Athlete_Monitoring?file={value}", id="someid_doesnt_matter")

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

    
