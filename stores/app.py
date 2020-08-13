
import pandas as pd   
import dash 
import dash_table as dt
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from get_stores import get_stores
from dash_extensions import Download
from dash_extensions.snippets import send_data_frame


external_stylesheets = ["https://codepen.io/chriddyp/pen/bWLwgP.css"]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

#---------------------------------------------------------------
app.layout = html.Div([
    dcc.Textarea(
        id='textarea-state-example',
        style={'width': '5%', 'height': 200},
    ),
    html.Br(),
    #html.Button('Submit', id='textarea-state-example-button', n_clicks=0),
    html.Button("Download csv", id="btn", n_clicks=0), 
    Download(id="download"),
    #html.Div(id="table")
])

#---------------------------------------------------------------
#@app.callback(
#    Output('table', 'children'),
#    [Input('textarea-state-example-button', 'n_clicks')],
#    [State('textarea-state-example', 'value')]
#)
@app.callback(
    Output("download", "data"), 
    [Input("btn", "n_clicks")],
    [State('textarea-state-example', 'value')]
)

def update_output(n_clicks, zip_codes):
    if zip_codes is None:
        raise PreventUpdate
    else:
        zip_codes = ''.join(e for e in zip_codes if e.isalnum())
        zip_codes = [zip_codes[i:i+5] for i in range(0, len(zip_codes), 5)]
        data=[]
        for z in zip_codes:
            data.append(get_stores(z))
        df=pd.concat(data)
        #data = df.to_dict('rows')
        #columns =  [{"name": i, "id": i,} for i in (df.columns)]
        return send_data_frame(df.to_csv, filename="zip_codes.csv")#dt.DataTable(data=data, columns=columns)

if __name__ == '__main__':
    app.run_server(debug=True)