from flask import Flask, jsonify, render_template, Response
import requests
from datetime import datetime
import time
import csv
from io import StringIO

app = Flask(__name__, template_folder="../templates", static_folder="../static")

CACHE = {
    "bitcoin": 0,
    "ethereum": 0,
    "last_updated": 0
}

COINGECKO_BASE = "https://api.coingecko.com/api/v3"


@app.route("/")
def index():
    return render_template("index.html")


def fetch_prices():
    url = f"{COINGECKO_BASE}/simple/price"
    params = {
        "ids": "bitcoin,ethereum",
        "vs_currencies": "usd"
    }
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    return r.json()


@app.route("/api/prices")
def get_prices():
    try:
        if time.time() - CACHE["last_updated"] > 60:
            prices = fetch_prices()
            CACHE["bitcoin"] = prices["bitcoin"]["usd"]
            CACHE["ethereum"] = prices["ethereum"]["usd"]
            CACHE["last_updated"] = time.time()

        return jsonify(CACHE)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/chart-data/<coin_id>")
def chart_data(coin_id):
    try:
        url = f"{COINGECKO_BASE}/coins/{coin_id}/market_chart"
        params = {"vs_currency": "usd", "days": 30}
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()

        prices = r.json()["prices"]
        data = [
            {
                "date": datetime.fromtimestamp(p[0] / 1000).strftime("%Y-%m-%d"),
                "price": p[1]
            }
            for p in prices
        ]

        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/download-csv")
def download_csv():
    try:
        btc = requests.get(
            f"{COINGECKO_BASE}/coins/bitcoin/market_chart",
            params={"vs_currency": "usd", "days": 30},
            timeout=10
        ).json()["prices"]

        eth = requests.get(
            f"{COINGECKO_BASE}/coins/ethereum/market_chart",
            params={"vs_currency": "usd", "days": 30},
            timeout=10
        ).json()["prices"]

        si = StringIO()
        writer = csv.writer(si)
        writer.writerow(["date", "bitcoin_usd", "ethereum_usd"])

        for i in range(min(len(btc), len(eth))):
            date = datetime.fromtimestamp(btc[i][0] / 1000).strftime("%Y-%m-%d")
            writer.writerow([date, btc[i][1], eth[i][1]])

        return Response(
            si.getvalue(),
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment; filename=crypto_30_day_prices.csv"}
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500
