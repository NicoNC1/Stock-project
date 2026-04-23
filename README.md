# Stock Performance Analytics Project

This project is a data-driven analytics solution focused on comparing and analyzing stock market performance using historical data from Yahoo Finance.

The objective is to evaluate how different stocks perform over time based on:
- Price development
- Returns
- Volatility

The goal is to support data-driven decision-making by transforming raw financial data into actionable business insights.

## Project Architecture

The project uses a simple pipeline:
1. Python extracts and processes stock data from Yahoo Finance.
2. A Flask REST API exposes structured datasets and summary metrics.
3. The API is hosted on Render.
4. Power BI consumes the API endpoints for interactive reporting.

This makes it possible to move from raw market data to visual and decision-ready analytics.

## API Endpoints

Base URL (Render):
- https://<your-service>.onrender.com

Health and service info:
- GET /

Historical price data (with daily return):
- GET /history/<ticker>?period=1y&interval=1d

Single stock metrics:
- GET /metrics/<ticker>?period=1y&interval=1d

Backward compatible raw history endpoint:
- GET /stock/<ticker>?period=1y&interval=1d

Compare multiple stocks (query string):
- GET /compare?tickers=AAPL,MSFT,NVDA&period=1y&interval=1d

Compare two stocks (backward compatible route):
- GET /compare/<ticker1>/<ticker2>?period=1y&interval=1d

## Key Metrics Provided

The metrics endpoint and compare endpoints return:
- Total return
- Annualized return
- Daily volatility
- Annualized volatility
- Maximum drawdown
- Start and end close prices

## Deploy Notes (Render)

Use:
- Build command: pip install -r requirements.txt
- Start command: gunicorn app:app

Required files in repository:
- app.py
- requirements.txt
- Procfile

## Power BI Integration

In Power BI Desktop:
1. Use Get Data -> Web.
2. Enter one of the API endpoint URLs.
3. Expand the JSON records and build visuals for trend, return, and risk comparison.

Suggested visuals:
- Line chart: price development over time
- Bar chart: total return by ticker
- Scatter/bubble chart: return vs volatility
- Table: key metrics per stock
