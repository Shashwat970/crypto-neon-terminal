from flask import Flask, jsonify, render_template, Response
from pycoingecko import CoinGeckoAPI
from datetime import datetime
import time
import csv
from io import StringIO
import json
import plotly
import plotly.graph_objs as go

app = Flask(__name__, template_folder="../templates", static_folder="../static")
cg = CoinGeckoAPI()

# In-memory cache (works per request container)
data_cache = {
    "bitcoin": 0,
    "ethereum": 0,
    "last_updated": 0
}


@app.route("/")
def index():
    return render_template("index.html")


def update_crypto_data():
    prices = cg.get_price(
        ids=["bitcoin", "ethereum"],
        vs_currencies="usd"
    )
    data_cache["bitcoin"] = prices["bitcoin"]["usd"]
    data_cache["ethereum"] = prices["ethereum"]["usd"]
    data_cache["last_updated"] = time.time()


@app.route("/api/prices")
def get_prices():
    if time.time() - data_cache["last_updated"] > 90:
        update_crypto_data()
    return jsonify(data_cache)


@app.route("/api/chart-data/<coin_id>")
def chart_data(coin_id):
    data = cg.get_coin_market_chart_by_id(
        id=coin_id,
        vs_currency="usd",
        days=30
    )

    x = [
        datetime.fromtimestamp(p[0] / 1000).strftime("%Y-%m-%d")
        for p in data["prices"]
    ]
    y = [p[1] for p in data["prices"]]

    graph = [go.Scatter(
        x=x,
        y=y,
        mode="lines",
        name=coin_id.capitalize()
    )]

    return json.dumps(graph, cls=plotly.utils.PlotlyJSONEncoder)


@app.route("/api/download-csv")
def download_csv():
    btc = cg.get_coin_market_chart_by_id("bitcoin", "usd", 30)
    eth = cg.get_coin_market_chart_by_id("ethereum", "usd", 30)

    si = StringIO()
    writer = csv.writer(si)
    writer.writerow(["date", "bitcoin_usd", "ethereum_usd"])

    for i in range(min(len(btc["prices"]), len(eth["prices"]))):
        date = datetime.fromtimestamp(
            btc["prices"][i][0] / 1000
        ).strftime("%Y-%m-%d")

        writer.writerow([
            date,
            btc["prices"][i][1],
            eth["prices"][i][1]
        ])

    return Response(
        si.getvalue(),
        mimetype="text/csv",
        headers={
            "Content-Disposition":
            "attachment; filename=crypto_30_day_prices.csv"
        }
    )


# Required for Vercel
def handler(environ, start_response):
    return app(environ, start_response)
