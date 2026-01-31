from flask import Flask, jsonify, render_template, Response
from pycoingecko import CoinGeckoAPI
from datetime import datetime
import time
import csv
from io import StringIO

app = Flask(__name__, template_folder="../templates", static_folder="../static")
cg = CoinGeckoAPI()

# Cache
cache = {
    "bitcoin": 0,
    "ethereum": 0,
    "last_updated": 0
}

@app.route("/")
def index():
    return render_template("index.html")

def update_prices():
    prices = cg.get_price(ids=["bitcoin", "ethereum"], vs_currencies="usd")
    cache["bitcoin"] = prices["bitcoin"]["usd"]
    cache["ethereum"] = prices["ethereum"]["usd"]
    cache["last_updated"] = time.time()

@app.route("/api/prices")
def prices():
    if time.time() - cache["last_updated"] > 60:
        update_prices()
    return jsonify(cache)

@app.route("/api/chart-data/<coin>")
def chart_data(coin):
    data = cg.get_coin_market_chart_by_id(
        id=coin,
        vs_currency="usd",
        days=30
    )

    return jsonify([
        {
            "date": datetime.fromtimestamp(p[0]/1000).strftime("%Y-%m-%d"),
            "price": p[1]
        }
        for p in data["prices"]
    ])

@app.route("/api/download-csv")
def download_csv():
    btc = cg.get_coin_market_chart_by_id("bitcoin", "usd", 30)["prices"]
    eth = cg.get_coin_market_chart_by_id("ethereum", "usd", 30)["prices"]

    si = StringIO()
    writer = csv.writer(si)
    writer.writerow(["date", "bitcoin_usd", "ethereum_usd"])

    for i in range(min(len(btc), len(eth))):
        writer.writerow([
            datetime.fromtimestamp(btc[i][0]/1000).strftime("%Y-%m-%d"),
            btc[i][1],
            eth[i][1]
        ])

    return Response(
        si.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=crypto_30_days.csv"}
    )
