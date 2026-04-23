from flask import Flask, jsonify, request
import yfinance as yf
import pandas as pd
import math

app = Flask(__name__)


TRADING_DAYS_PER_YEAR = 252


def _download_history(ticker, period="1y", interval="1d"):
    data = yf.download(
        ticker,
        period=period,
        interval=interval,
        auto_adjust=True,
        progress=False,
    )

    if data.empty:
        return pd.DataFrame()

    data = data.reset_index()

    if "Date" in data.columns:
        data["Date"] = pd.to_datetime(data["Date"]).dt.strftime("%Y-%m-%d")

    return data


def _calculate_metrics(data):
    if data.empty or "Close" not in data.columns:
        return {}

    close = data["Close"].dropna()
    if close.empty:
        return {}

    returns = close.pct_change().dropna()
    total_return = float(close.iloc[-1] / close.iloc[0] - 1)

    n_returns = len(returns)
    annualized_return = None
    if n_returns > 0:
        annualized_return = float((1 + total_return) ** (TRADING_DAYS_PER_YEAR / n_returns) - 1)

    daily_volatility = float(returns.std()) if n_returns > 1 else None
    annualized_volatility = None
    if daily_volatility is not None:
        annualized_volatility = float(daily_volatility * math.sqrt(TRADING_DAYS_PER_YEAR))

    running_max = close.cummax()
    drawdown = (close / running_max) - 1
    max_drawdown = float(drawdown.min())

    return {
        "observations": int(len(close)),
        "start_close": float(close.iloc[0]),
        "end_close": float(close.iloc[-1]),
        "total_return": total_return,
        "annualized_return": annualized_return,
        "daily_volatility": daily_volatility,
        "annualized_volatility": annualized_volatility,
        "max_drawdown": max_drawdown,
    }


def _history_records(data):
    if data.empty:
        return []

    working = data.copy()
    if "Close" in working.columns:
        working["DailyReturn"] = working["Close"].pct_change()

    return working.to_dict(orient="records")


@app.route("/")
def home():
    return jsonify(
        {
            "service": "Stock Analytics API",
            "status": "running",
            "endpoints": {
                "history": "/history/<ticker>?period=1y&interval=1d",
                "metrics": "/metrics/<ticker>?period=1y&interval=1d",
                "compare": "/compare?tickers=AAPL,MSFT&period=1y&interval=1d",
            },
        }
    )


@app.route("/history/<ticker>")
def history(ticker):
    period = request.args.get("period", "1y")
    interval = request.args.get("interval", "1d")
    data = _download_history(ticker, period=period, interval=interval)

    if data.empty:
        return jsonify({"error": f"No data found for ticker '{ticker.upper()}'."}), 404

    return jsonify(
        {
            "ticker": ticker.upper(),
            "period": period,
            "interval": interval,
            "rows": len(data),
            "data": _history_records(data),
        }
    )


@app.route("/metrics/<ticker>")
def metrics(ticker):
    period = request.args.get("period", "1y")
    interval = request.args.get("interval", "1d")
    data = _download_history(ticker, period=period, interval=interval)

    if data.empty:
        return jsonify({"error": f"No data found for ticker '{ticker.upper()}'."}), 404

    return jsonify(
        {
            "ticker": ticker.upper(),
            "period": period,
            "interval": interval,
            "metrics": _calculate_metrics(data),
        }
    )


@app.route("/stock/<ticker>")
def stock(ticker):
    period = request.args.get("period", "1y")
    interval = request.args.get("interval", "1d")
    data = _download_history(ticker, period=period, interval=interval)

    if data.empty:
        return jsonify({"error": f"No data found for ticker '{ticker.upper()}'."}), 404

    return jsonify(_history_records(data))


@app.route("/compare")
def compare_multi():
    tickers_raw = request.args.get("tickers", "")
    period = request.args.get("period", "1y")
    interval = request.args.get("interval", "1d")

    tickers = [t.strip().upper() for t in tickers_raw.split(",") if t.strip()]
    if len(tickers) < 2:
        return jsonify({"error": "Provide at least two tickers via ?tickers=AAPL,MSFT"}), 400

    comparison = []
    for ticker in tickers:
        data = _download_history(ticker, period=period, interval=interval)
        if data.empty:
            continue

        comparison.append(
            {
                "ticker": ticker,
                "metrics": _calculate_metrics(data),
            }
        )

    if not comparison:
        return jsonify({"error": "No data found for the requested tickers."}), 404

    return jsonify(
        {
            "period": period,
            "interval": interval,
            "comparison": comparison,
        }
    )


@app.route("/compare/<ticker1>/<ticker2>")
def compare(ticker1, ticker2):
    period = request.args.get("period", "1y")
    interval = request.args.get("interval", "1d")

    data1 = _download_history(ticker1, period=period, interval=interval)
    data2 = _download_history(ticker2, period=period, interval=interval)

    if data1.empty and data2.empty:
        return jsonify({"error": "No data found for either ticker."}), 404

    payload = {
        "period": period,
        "interval": interval,
        "comparison": [],
    }

    if not data1.empty:
        payload["comparison"].append(
            {"ticker": ticker1.upper(), "metrics": _calculate_metrics(data1)}
        )
    if not data2.empty:
        payload["comparison"].append(
            {"ticker": ticker2.upper(), "metrics": _calculate_metrics(data2)}
        )

    return jsonify(payload)


if __name__ == "__main__":
    app.run(debug=True)
