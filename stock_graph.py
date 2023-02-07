import base64
from dash import Dash, html, dcc, Output, Input, State
from datetime import datetime
import pandas as pd
import yfinance as yf


def b64_image(image_filename):
    with open(image_filename, 'rb') as f:
        image = f.read()
    return 'data:image/png;base64,' + base64.b64encode(image).decode('utf-8')

def main():
    image_path = 'assets/stock.png' 
    filename = "nasdaq_screener.csv"
    data = pd.read_csv(filename)

    data_options = []
    for element in data.index:
        data_options.append({"label": data["Name"][element], "value": data["Symbol"][element]})


    heading = html.Div([html.Img(src=b64_image(image_path),
                                 className="header-image"),
                        html.H1(
                            children="Stock Viewer Web App",
                            className="header-title",
                            ),                            
                         html.P(children="Stocks viewer graph",
                                className="header-subtitle")])

    stock_picker = html.Div([html.H2('Select stocks:'),
                            dcc.Dropdown(
                                id="dropdown",
                                options=data_options,
                                value = ["GOOG"],
                                multi=True
                            )])
    date_picker = html.Div([html.H2("Select dates:"),
                            dcc.DatePickerRange(
                                id="datepicker",
                                min_date_allowed = datetime(2010, 1, 1),
                                max_date_allowed=datetime(2023, 2, 1),
                                start_date=datetime(2022, 1, 1),
                                end_date=datetime(2023, 1, 1)
                            )])
    button = html.Div([html.Button(
                            id="submit-button",
                            n_clicks=0,
                            children="Submit",
                            className="submit-button"
                        )])
    graph = dcc.Graph(id="stock-graph")

    external_stylesheets = [
        {
            "href": "https://fonts.googleapis.com/css2?"
                "family=Lato:wght@400;700&display=swap",
            "rel": "stylesheet",
        },
    ]

    app = Dash(__name__, external_stylesheets=external_stylesheets)
    app.title = "Stock Graphs"
    app.layout = html.Div([heading, stock_picker, date_picker, button, graph])

    @app.callback(Output("stock-graph", "figure"),
              [Input("submit-button", "n_clicks")],
              [State("dropdown", "value"), 
              State("datepicker", "start_date"),
              State("datepicker", "end_date")])
    def update_graph(number_of_clicks, stocks, start_date, end_date):
        start = datetime.strptime(start_date[:10], "%Y-%m-%d")
        end = datetime.strptime(end_date[:10], "%Y-%m-%d")
        graph_data = []
        for stock in stocks:
            new_df = yf.download(tickers=[stock], start=start, end=end)
            new_df.head()
            dates = []
            for row in range(len(new_df)):
                new_date = str(new_df.index[row])
                new_date = new_date[0:10]
                dates.append(new_date)
            
            new_df["Date"] = dates
            graph_data.append({
                "x": new_df["Date"],
                "y": new_df["Adj Close"],
                "name": stock
            })
        
        figure = {
            "data": graph_data,
            "layout": {
                "title": "Stock Data"
            }
        }

        return figure

    app.run_server(port = 5050)

if __name__ == '__main__':
    main()