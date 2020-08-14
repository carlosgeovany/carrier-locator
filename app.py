import pandas as pd   
import dash 
import dash_table as dt
import dash_core_components as dcc
import dash_html_components as html
import folium
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from get_stores import get_stores
from dash_extensions import Download
from dash_extensions.snippets import send_data_frame
from maps import *

external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = 'Carrier Locator'

server = app.server

#---------------------------------------------------------------
app.layout = html.Div(
    children=[
        html.Div(style={'padding': 5, 'margin': 20},
            children=[
                html.H1("Carrier Locator")
            ]
        ),
        html.Div(style={'padding': 5, 'margin': 20},
            children=[
                html.H2("Type the zip codes in the text box, one zip code per line:"),
                dcc.Textarea(
                    id='textarea_state',
                    style={'width': '5%', 'height': 200}
                ),
            ]
        ),
        html.Div(style={'padding': 5, 'margin': 20},
            children=[
                html.Button('Submit', id='button_submit', n_clicks=0),
                html.Button("Download csv", id="button_download", n_clicks=0)
            ]
        ),
        html.Iframe(id='map', srcDoc=open('locations.html', 'r').read()),
        html.Table(id="table", style={'padding': 5, 'margin': 20, 'position':'absolute', 'top':100})
        
    ]
)
#---------------------------------------------------------------
@app.callback(
    [
        Output('table', 'children'),
        Output('map', 'srcDoc')
    ],
    [Input('button_submit', 'n_clicks')],
    [State('textarea_state', 'value')]
)

def get_table(n_clicks, zip_codes):
    if zip_codes is None:
        raise PreventUpdate
    else:
        zip_codes = ''.join(e for e in zip_codes if e.isalnum())
        zip_codes = [zip_codes[i:i+5] for i in range(0, len(zip_codes), 5)]
        data = []
        for z in zip_codes:
            data.append(get_stores(z))
        df=pd.concat(data)
        map_folium(zip_codes, df)
        data = df.to_dict('records')
        columns =  [{"name": i, "id": i,} for i in (df.columns)]
        return dt.DataTable(
                            data=data, 
                            columns=columns,                            
                            style_cell={
                                'overflow': 'hidden',
                                'textOverflow': 'ellipsis',
                                'maxWidth': 88
                            }
        ),open('locations.html', 'r').read()
        
                            #send_data_frame(df.to_csv, filename="zip_codes.csv")

#@app.callback(
#    Output("download", "data"), 
#    [Input("button_download", "n_clicks")]
#)


if __name__ == '__main__':
    app.run_server(debug=True)

