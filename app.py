# app.py
import dash
from dash import dcc
from dash import html
from flask import Flask

server = Flask(__name__)
app = dash.Dash(
    __name__,
    server=server,
)

app.layout = html.Div([
    dcc.Graph(id='example-graph', figure={
        'data': [{'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'bar', 'name': 'SF'},
                 {'x': [1, 2, 3], 'y': [2, 4, 5], 'type': 'bar', 'name': u'Montréal'},
                 ],
        'layout': {'title': 'Dash Data Visualization'}
    })
])

if __name__ == '__main__':
    app.run_server(debug=True)
