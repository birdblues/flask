import json
import numpy as np
import yfinance as yf
import pandas as pd
import pandas_ta as ta
import random
from pprint import pprint
from datetime import datetime, timedelta

import dash_tvlwc
import dash
from dash.dependencies import Input, Output, State
from dash import html, dcc, ctx

from dash_tvlwc.types import ColorType, SeriesType
from data_generator import generate_random_ohlc, generate_random_series

df = yf.Ticker('KRW=X').history(period='24mo', interval='1d')[['Open', 'High', 'Low', 'Close', 'Volume']]
df = df.reset_index()
df.columns = ['time','open','high','low','close','volume']
df['time'] = df['time'].dt.strftime('%Y-%m-%d')  
# pprint(df)
data = [json.loads(
    df.filter(['time','close'], axis=1)
      .rename(columns={"close": "value"})
      .to_json(orient = "records"))]
# pprint(data)

main_panel = [
    html.Div(style={'position': 'relative', 'width': '100%', 'height': '100%'}, children=[
        html.Div(children=[
            dash_tvlwc.Tvlwc(
                id='tv-chart-1',
                seriesData=data,
                seriesTypes=[SeriesType.Area],
                width='100%',
                chartOptions={
                    "handleScale": {
                        "axisPressedMouseMove": False,
                        "mouseWheel": True,
                        "pinch": False
                    },
                    "timeScale": {
                        "borderColor": "rgba(197, 203, 206, 0.8)",
                        "barSpacing": 10,
                        "minBarSpacing": 2,
                        "timeVisible": False,
                        "secondsVisible": False,
                    },
                    "watermark": {
                        "visible": True,
                        "fontSize": 50,
                        "horzAlign": 'center',
                        "vertAlign": 'center',
                        "color": 'rgba(255, 255, 255, 0.2)',
                        "text": 'USD/KRW',
                    },
                    "layout": {
                        "background": {
                            "type": 'solid',
                            "color": '#131722'
                        },
                        "textColor": '#d1d4dc',
                    },
                    "grid": {
                        "vertLines": {
                            "color": 'rgba(42, 46, 57, 0)',
                        },
                        "horzLines": {
                            "color": 'rgba(42, 46, 57, 0.6)',
                        }
                    },
                    'localization': {
                        'locale': 'en-US',
                        'priceFormatter': "(function(price) { return '$' + price.toFixed(2); })"
                    }
                },
            ),
            
        ], style={'width': '100%', 'height': '100%', 'left': 0, 'top': 0}),
        html.Div(id='chart-info', children=[
            html.Span(id='chart-price', style={'fontSize': '60px', 'fontWeight': 'bold'}),
            html.Span(id='chart-date', style={'fontSize': 'small'}),
        ], style={'position': 'absolute', 'left': 0, 'top': 0, 'zIndex': 10, 'color': 'white', 'padding': '0px'})
    ]),
   
]

app = dash.Dash(__name__, external_stylesheets=['./assets/stylesheet.css'])
app.layout = html.Div([
    dcc.Interval(id='timer', interval=500),
    html.Div(className='container', children=[
        html.Div(className='main-container', children=[
            html.Div(children=main_panel),
        ]),
    ])
])

# callbacks to demo
@app.callback(
    [
        Output('tv-chart-1', 'chartOptions'),
        Output('chart-info', 'style'),
    ],
    [Input('change-theme', 'n_clicks')],
    [
        State('tv-chart-1', 'chartOptions'),
        State('chart-info', 'style'),
    ],
    prevent_initial_call=True
)

@app.callback(
    [
        Output('tv-chart-1', 'seriesData'),
        Output('tv-chart-1', 'seriesTypes'),
    ],
    [
        Input('change-chart-type', 'n_clicks'),
        Input('timer', 'n_intervals')
    ],
    [
        State('tv-chart-1', 'seriesData'),
        State('tv-chart-1', 'seriesTypes'),
    ],
    prevent_initial_call=True
)
@app.callback(
    [
        Output('chart-date', 'children'),
        Output('chart-price', 'children'),
    ],
    [Input('tv-chart-1', 'crosshair')],
    [State('tv-chart-1', 'seriesTypes')],
    prevent_initial_call=True
)
def crosshair_move(crosshair, series_types):
    time = crosshair.get('time')
    prices = crosshair['seriesPrices']

    if time is not None:
        time = datetime(time['year'], time['month'], time['day']).strftime('%Y-%m-%d') if time is not None else time
        time = f'{time}' if time is not None else None

    if prices:
        if series_types == [SeriesType.Candlestick]:
            prices = f"{prices['0']['close']:.2f}"
        else:
            prices = f"{prices['0']:.2f}"

    if not time and not prices:
        time = 'Hover on the plot to see date and price details.'

    return [time, prices]

server = app.server

if __name__ == '__main__':
    app.run_server(debug=True)