import dash as ds
from dash.exceptions import PreventUpdate
from dash import html
from dash import dcc
from dash.dependencies import Input, Output, State
import glob
import pandas as pd
from urllib import parse
from utils import accesslink, config, save_config, CONFIG_FILENAME

from app import app

layout = html.Div([
    html.Div([
        html.H2('Login result:'),
        html.Span(id='result', children='')
    ]),
     html.Div(id="hidden_div_for_redirect_callback")
])

@app.callback(
    Output("result", "children"),
    Input("url", "href"))
def callback(href):
    query = parse.urlparse(href).query
    parameters = parse.parse_qs(query)

    token_response = accesslink.get_access_token(parameters['code'][0])

    #
    # Save the user's id and access token to the configuration file.
    #
    config["refresh_token"] = token_response["refresh_token"]
    config["access_token"] = token_response["access_token"]
    save_config(config, CONFIG_FILENAME)