from os import path
from dash import dcc
from dash import html
from dash.dependencies import Input, Output

from app import app
from pages import Athlete_Monitoring ,data_choice,localdata

app.layout= html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

@app.callback(Output('page-content', 'children'),
            Input('url', 'pathname'))
def display_page(pathname):
    print(pathname)
    if pathname == '/pages/Athlete_Monitoring':
        return Athlete_Monitoring.layout
    if pathname == '/pages/data_choice':
        return data_choice.layout
    if pathname =='/pages/localdata':
        return localdata.layout
    return '404'

if __name__=='__main__':
    app.run_server(debug=True)