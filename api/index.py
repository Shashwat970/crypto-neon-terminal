from flask import Flask, jsonify, render_template, Response
import requests
import pandas as pd
import time

app = Flask(__name__, template_folder="../templates", static_folder="../static")

CACHE = {
    "data": [],
    "last_updated": 0
}

COINS = ["bitcoin", "ethereum"]

def fetch_crypto_data():
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "ids": ",".join(COINS),
        "order": "market_cap_desc",
        "per_page": 2,
        "page": 1,
        "sparkline": False
    }
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    return response.json()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/prices")
def prices():
    try:
        if time.time() - CACHE["last_updated"] > 60:
            data = fetch_crypto_data()
            CACHE["data"] = data
            CACHE["last_updated"] = time.time()
        return jsonify(CACHE["data"])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/api/download")
def download_csv():
    try:
        if not CACHE["data"]:
            CACHE["data"] = fetch_crypto_data()

        df = pd.DataFrame(CACHE["data"])
        csv_data = df.to_csv(index=False)

        return Response(
            csv_data,
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment; filename=crypto_data.csv"}
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

