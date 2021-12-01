import dash as ds
from dash.exceptions import PreventUpdate
from dash import html
from dash import dcc
from dash.dependencies import Input, Output, State
import glob
import pandas as pd
from urllib import parse
import utils

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

    utils.accesslink.get_access_token(refresh=False, authorization_code=parameters['code'][0])

    return dcc.Location(href="/pages/data_choice?data=polar", id="some-id")