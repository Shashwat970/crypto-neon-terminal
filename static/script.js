async function refreshData() {
    const res = await fetch("/api/prices");
    const data = await res.json();

    document.getElementById("bitcoin-price").innerText =
        `$${data.bitcoin.toLocaleString()}`;
    document.getElementById("ethereum-price").innerText =
        `$${data.ethereum.toLocaleString()}`;

    renderChart("bitcoin", "bitcoin-chart");
    renderChart("ethereum", "ethereum-chart");
}

async function renderChart(coin, elementId) {
    const res = await fetch(`/api/chart-data/${coin}`);
    const data = await res.json();

    Plotly.newPlot(
        elementId,
        [{
            x: data.map(d => d.date),
            y: data.map(d => d.price),
            type: "scatter",
            mode: "lines",
            line: { color: "#00ff88" }
        }],
        {
            margin: { t: 20 },
            paper_bgcolor: "black",
            plot_bgcolor: "black",
            font: { color: "#00ff88" }
        },
        {
            title: 'Scatter Line Chart for ' + coin,
            xaxis: { title: 'Date' },
            yaxis: { title: 'Coin Price (USD)' }
        },
        { displayModeBar: false }
    );
}

document.getElementById("refresh-btn").onclick = refreshData;
document.getElementById("csv-btn").onclick = () => {
    window.location.href = "/api/download-csv";
};

refreshData();
setInterval(refreshData, 60000);
