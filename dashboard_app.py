from flask import Flask, render_template
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

# Assuming you have already created your Flask app instance
server = app = Flask(__name__)

# Create your Dash app
dash_app = dash.Dash(__name__, server=server, url_base_pathname="/salloc/dashboard/")

dash_app.layout = html.Div([
    dcc.Input(id="input-box", type="text", value=""),
    html.Div(id="output-container", children=[]),
])

@dash_app.callback(
    Output("output-container", "children"),
    [Input("input-box", "value")]
)
def update_output(value):
    return f"You entered: {value}"

if __name__ == "__main__":
    app.run_server(debug=True)