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
        types = ("data/*.parquet", "data/*.csv", "data/*.xls", "data/*.fea", "data/*.npy", "data/*.json")
        files_grabbed = []
        for files in types:
            files_grabbed.extend(glob.glob(files))
        return [{"label": file.replace("data\\", ""), "value": file} for file in files_grabbed]
    raise PreventUpdate

@app.callback(Output("hidden_div_for_redirect_callback", "children"),
                Input("local_dropdown", "value"))
def read_selected_file(value):
    if value == None:
        raise PreventUpdate
    return dcc.Location(href=f"/pages/Athlete_Monitoring?file={value}", id="someid_doesnt_matter")