import dash
from dash import dcc, html, Input, Output, State
from tkinter import filedialog, Tk
from data_csv import DataCSV
from parameter_config import ParameterConfig
from retention_calculator import RetentionCalculator

# file picker — reuse tkinter just for selecting the file
root = Tk()
root.withdraw()
filepath = filedialog.askopenfilename(
    title="Select your enrollment data file (CSV only)",
    filetypes=[("CSV files", "*.csv")]
)

if not filepath:
    print("No file was selected.")
    exit()

file = DataCSV(filepath)
file.load()
file.clean()
df = file.getdf()

baseyear = int(input("Enter the base year (2025 for SY24-25): "))
numyears = int(input("Enter the number of years forward: "))
loomistoggle = input("Loomis K-2, Longwood 3-8? (y/n) Otherwise Loomis K-3, Longwood 4-8: ").lower() == 'y'

config = ParameterConfig(baseyear, numyears, loomistoggle, gradefilter=None)
calculator = RetentionCalculator(df, config)

app = dash.Dash(__name__)

app.layout = html.Div([
    html.Button("← Back to overview", id="back-button", style={"display": "none"}),
    dcc.Graph(id="retention-graph"),
    dcc.Store(id="current-view", data="overview")
])

@app.callback(
    Output("retention-graph", "figure"),
    Output("back-button", "style"),
    Output("current-view", "data"),
    Input("retention-graph", "clickData"),
    Input("back-button", "n_clicks"),
    State("current-view", "data"),
    prevent_initial_call=False
)
def update_graph(click_data, back_clicks, current_view):
    triggered = dash.callback_context.triggered_id

    if triggered == "back-button":
        return calculator.graph(), {"display": "none"}, "overview"

    if triggered == "retention-graph" and click_data and current_view == "overview":
        school_name = click_data["points"][0]["customdata"]
        fig = calculator.school_drilldown(school_name)
        return fig, {"display": "inline-block"}, "drilldown"

    return calculator.graph(), {"display": "none"}, "overview"

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)