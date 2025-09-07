from dash import Dash, html, Input, Output, dash_table, dcc, callback, page_container, register_page
import pandas as pd
from datetime import datetime

def load_data():
    # Get the current time and round down to the nearest quarter hour
    now = datetime.now()
    minute = (now.minute // 15) * 15
    time_str = now.replace(minute=minute, second=0, microsecond=0).strftime("%H%M")
    filename = "data/rainfall/latest_rainfall.csv"
    try:
        return pd.read_csv(filename)
    except FileNotFoundError:
        # If the file does not exist, return an empty DataFrame or handle as needed
        return pd.read_csv("data/rainfall/rainfall_init.csv")

app = Dash(__name__, use_pages=True, suppress_callback_exceptions=True)

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dcc.Link('Home', href='/', style={'marginRight': '20px'}),
    dcc.Link('Rainfall Data', href='/rainfall'),
    html.Hr(),
    page_container
])

# Home page
register_page(
    __name__,
    path='/',
    layout=html.Div([
        html.H2('Welcome to the Weather Dashboard'),
        html.P('Use the navigation links above to view rainfall data.')
    ])
)

# Rainfall data page
def rainfall_layout():
    return html.Div([
        html.H4(id='live_time'),
        html.P(id='table_out'),
        dash_table.DataTable(
            id='table',
            columns=[],
            data=[],
            style_cell=dict(textAlign='left'),
            style_header=dict(backgroundColor="paleturquoise"),
            style_data=dict(backgroundColor="lavender")
        ),
        dcc.Interval(
            id='interval-component',
            interval=15*60*1000, # 15 minutes in milliseconds
            n_intervals=0
        )
    ])

register_page(
    'rainfall',
    path='/rainfall',
    layout=rainfall_layout()
)

@app.callback(
    [Output('live_time', 'children'),
     Output('table', 'data'),
     Output('table', 'columns')],
    Input('interval-component', 'n_intervals')
)
def update_table(n):
    df = load_data()
    minute = (datetime.now().minute // 15)*15
    nearest_time = datetime.now().replace(minute=minute, second=0, microsecond=0)
    nearest_time = nearest_time.strftime("%Y-%m-%d %H:%M")
    columns = [{"name": i, "id": i} for i in df.columns]
    return f'Rainfall in the past hour from automatic weather station as at {nearest_time}', df.to_dict('records'), columns

app.run(debug=True)