import dash as ds
from dash.exceptions import PreventUpdate
from dash import html
from dash import dcc
from dash.dependencies import Input, Output, State
import utils
import glob
import pandas as pd

from app import app

layout = html.Div([
    html.Div([
        html.H2(
            'Data needs to be stored in: Athlete_Monitoring\dash_server\data'),
        dcc.Dropdown(
            id='local_dropdown'
        ),
    ]),
    html.Div(id='data_display', children=''),
    html.Div(id="hidden_div_for_redirect_callback")
])

# dynamically assigns dropdown options for "local_dropdown" in form of file names
@app.callback(Output('local_dropdown', 'options'),
              Input('data_dropdown', 'value'))
def data_display(value):
    if value == "local":
        teams = utils.api.get_teams()
        team_name = None
        files_grabbed = []
        for i, name in enumerate(teams):
            team_name = name["name"]
            types = (f"data/{team_name}/*.parquet", f"data/{team_name}/*.csv", f"data/{team_name}/*.xls",
                     f"data/{team_name}/*.fea", f"data/{team_name}/*.npy", f"data/{team_name}/*.json")
            for files in types:
                files_grabbed.extend(glob.glob(files))
        return [{"label": file.replace("data/", ""), "value": file} for file in files_grabbed]
    raise PreventUpdate

# loads Athlete_Monitoring page when file is choosen, includes filename in url


@app.callback(Output("hidden_div_for_redirect_callback", "children"),
              Input("local_dropdown", "value"))
def read_selected_file(value):
    if value == None:
        raise PreventUpdate
    return dcc.Location(href=f"/pages/Athlete_Monitoring?file={value}", id="someid_doesnt_matter")
