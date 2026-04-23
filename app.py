from flask import Flask
import yfinance as yf
import pandas as pd

app = Flask(__name__)


@app.route("/")
def home():
    return "Stock API is running"


@app.route("/stock/<ticker>")
def stock(ticker):
    data = yf.download(ticker, period="1y")
    data.reset_index(inplace=True)
    return data.to_json(orient="records")


@app.route("/compare/<ticker1>/<ticker2>")
def compare(ticker1, ticker2):
    data1 = yf.download(ticker1, period="1y")
    data2 = yf.download(ticker2, period="1y")

    data1["Ticker"] = ticker1
    data2["Ticker"] = ticker2

    combined = pd.concat([data1, data2])
    combined.reset_index(inplace=True)

    return combined.to_json(orient="records")


if __name__ == "__main__":
    app.run(debug=True)
