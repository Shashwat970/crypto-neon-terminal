from flask import Flask, jsonify, render_template
from pycoingecko import CoinGeckoAPI
import time
import json
import plotly
import plotly.graph_objs as go
from datetime import datetime
import csv
from io import StringIO
from flask import Response


app = Flask(__name__)
cg = CoinGeckoAPI()

# Cache to store the latest prices to avoid hitting API rate limits too often
data_cache = {
    "bitcoin": 0,
    "ethereum": 0,
    "last_updated": 0
}

@app.route('/api/download-csv')
def download_csv():
    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(['Coin', 'Price (USD)', 'Timestamp'])
    cw.writerow(['Bitcoin', data_cache['bitcoin'], data_cache['last_updated']])
    cw.writerow(['Ethereum', data_cache['ethereum'], data_cache['last_updated']])

    output = si.getvalue()
    return Response(
        output,
        mimetype='text/csv',
        headers={"Content-Disposition": "attachment;filename=crypto_prices.csv"}
    )


@app.route('/')
def index():
    return render_template('index.html')

def update_crypto_data():
    """Fetches real-time prices for BTC and ETH using pycoingecko."""
    try:
        # Fetching price for multiple IDs at once
        prices = cg.get_price(ids=['bitcoin', 'ethereum'], vs_currencies='usd')
        data_cache["bitcoin"] = prices['bitcoin']['usd']
        data_cache["ethereum"] = prices['ethereum']['usd']
        data_cache["last_updated"] = time.time()
        return data_cache
    except Exception as e:
        print(f"Error fetching data: {e}")
        return data_cache

@app.route('/api/prices')
def get_prices():
    """Endpoint for the frontend to fetch updated data."""
    # Only update if the cache is older than 90 seconds to respect free tier limits
    if time.time() - data_cache["last_updated"] > 90:
        update_crypto_data()
    return jsonify(data_cache)

@app.route('/api/chart-data/<coin_id>')
def chart_data(coin_id):
    # Fetch last 24 hours of data (minutely/hourly)
    data = cg.get_coin_market_chart_by_id(id=coin_id, vs_currency='usd', days='30')
    
    # Extract timestamps and prices
    prices = data['prices'] # List of [timestamp, price]
    x_data = [datetime.fromtimestamp(p[0]/1000).strftime('%Y-%m-%d %H:%M') for p in prices]
    y_data = [p[1] for p in prices]

    # Create a Plotly trace
    graph_data = [go.Scatter(
        x=x_data, 
        y=y_data, 
        name=coin_id.capitalize(),
        line=dict(color='#00ff88', width=2),
        fill='tozeroy',
        fillcolor='rgba(0, 255, 136, 0.1)'
    )]
    
    # Convert to JSON for JavaScript to read
    return json.dumps(graph_data, cls=plotly.utils.PlotlyJSONEncoder)

if __name__ == '__main__':
    app.run(debug=True)