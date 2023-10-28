import random
from datetime import datetime, timedelta

import dash_tvlwc
import dash
from dash.dependencies import Input, Output, State
from dash import html, dcc, ctx

from dash_tvlwc.types import ColorType, SeriesType
from data_generator import generate_random_ohlc, generate_random_series

main_panel = [
    html.Div(style={'position': 'relative', 'width': '100%', 'height': '100%'}, children=[
        html.Div(children=[
            dash_tvlwc.Tvlwc(
                id='tv-chart-1',
                seriesData=[generate_random_ohlc(100, n=100)],
                seriesTypes=[SeriesType.Candlestick],
                width='99%',
                chartOptions={
                    'layout': {
                        'background': {'type': ColorType.Solid, 'color': '#1B2631'},
                        'textColor': 'white',
                    },
                    'grid': {
                        'vertLines': {'visible': True, 'color': 'rgba(255,255,255,0.1)'},
                        'horzLines': {'visible': True, 'color': 'rgba(255,255,255,0.1)'},
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
        ], style={'position': 'absolute', 'left': 0, 'top': 0, 'zIndex': 10, 'color': 'white', 'padding': '10px'})
    ]),
   
]

chart_options = {
    'layout': {
        'background': {'type': 'solid', 'color': '#000000'},
        'textColor': 'white',
    },
    'grid': {
        'vertLines': {'visible': False},
        'horzLines': {'visible': False},
    },
    'localization': {'locale': 'en-US'}
}

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
def change_props(n, current_chart_options, chart_info_style):
    if current_chart_options['layout']['background']['color'] == '#1B2631':
        current_chart_options = {
            'layout': {
                'background': {'type': ColorType.Solid, 'color': '#dddddd'},
                'textColor': '#111111',
            },
            'grid': {
                'vertLines': {'visible': True, 'color': 'rgba(0,0,0,0.1)'},
                'horzLines': {'visible': True, 'color': 'rgba(0,0,0,0.1)'},
            }
        }
        chart_info_style['color'] = '#111111'
    else:
        current_chart_options = {
            'layout': {
                'background': {'type': ColorType.Solid, 'color': '#1B2631'},
                'textColor': 'white',
            },
            'grid': {
                'vertLines': {'visible': True, 'color': 'rgba(255,255,255,0.1)'},
                'horzLines': {'visible': True, 'color': 'rgba(255,255,255,0.1)'},
            },
        }
        chart_info_style['color'] = '#bbbbbb'

    return [current_chart_options, chart_info_style]


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
def change_props(n, interval, series_data, series_type):
    if ctx.triggered_id == 'timer':
        last_close_date = series_data[0][-1]['time']
        last_close_dt = datetime(last_close_date['year'], last_close_date['month'], last_close_date['day'])
        if series_type == [SeriesType.Candlestick]:
            new_datapoint = generate_random_ohlc(
                t0=(last_close_dt + timedelta(days=1)).strftime('%Y-%m-%d'),
                v0=series_data[0][-1]['close'], n=1
            )
            series_data[0].extend(new_datapoint)
        else:
            new_datapoint = generate_random_series(
                t0=(last_close_dt + timedelta(days=1)).strftime('%Y-%m-%d'),
                v0=series_data[0][-1]['value'], n=1
            )
            series_data[0].extend(new_datapoint)
        series_data[0] = series_data[0][1:]
        return [series_data, series_type]

    elif ctx.triggered_id == 'change-chart-type':
        if series_type == [SeriesType.Candlestick]:
            series_type = [SeriesType.Line]
            series_data = [generate_random_series(100, n=100)]
        else:
            series_type = [SeriesType.Candlestick]
            series_data = [generate_random_ohlc(100, n=100)]
        return [series_data, series_type]



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