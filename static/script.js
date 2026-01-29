async function refreshData() {
    const res = await fetch('/api/prices');
    const data = await res.json();

    document.getElementById('btc-price').innerText =
        `$${data.bitcoin.toLocaleString()}`;
    document.getElementById('eth-price').innerText =
        `$${data.ethereum.toLocaleString()}`;

    renderChart('bitcoin', 'btc-chart');
    renderChart('ethereum', 'eth-chart');
}

async function renderChart(coin, elementId) {
    const res = await fetch(`/api/chart-data/${coin}`);
    const data = await res.json();

    Plotly.newPlot(
        elementId,
        data,
        {
            margin: { t: 10, b: 30 },
            paper_bgcolor: 'rgba(0,0,0,0)',
            plot_bgcolor: 'rgba(0,0,0,0)'
        },
        { displayModeBar: false }
    );
}

document.querySelector('.btn-primary').onclick = refreshData;
document.querySelector('.btn-secondary').onclick = () => {
    window.location.href = '/api/download-csv';
};

refreshData();
setInterval(refreshData, 60000);
