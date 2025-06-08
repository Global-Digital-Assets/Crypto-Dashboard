let refreshInterval = 60;
let apiInterval = 15;
let countdown = refreshInterval;
let dashboardData = null;

function formatTimeAgo(ageSeconds) {
    if (ageSeconds == null) return 'N/A';
    if (ageSeconds < 60) return `${Math.round(ageSeconds)}s ago`;
    if (ageSeconds < 3600) return `${Math.floor(ageSeconds/60)}m ago`;
    return `${Math.floor(ageSeconds/3600)}h ago`;
}

function formatDashboard(data) {
    const { status, signals } = data;
    const now = new Date();
    let lastUpdate = status.last_signal_timestamp ? new Date(status.last_signal_timestamp) : null;
    let lastUpdateStr = lastUpdate ? lastUpdate.toISOString().replace('T', ' ').slice(0, 19) : 'N/A';
    let candleStatus = status.candle_update_active ? 'ACTIVE' : 'STALE';
    let candleClass = status.candle_update_active ? 'active' : 'stale';
    let candleAge = formatTimeAgo(status.candle_age_seconds);

    let out = `CRYPTO TRADING DASHBOARD\n========================\n`;
    out += `Last Update: ${lastUpdateStr}\n\n`;
    out += `Services:\n`;
    out += `- Buying Bot: ${status.buying_bot_status === 'UP' ? '✓ UP' : '✗ DOWN'}\n`;
    out += `- Analytics: ${status.analytics_status === 'UP' ? '✓ UP' : '✗ DOWN'}  \n`;
    out += `- Candles: ${candleStatus} (${candleAge})\n\n`;
    out += `Signals (15-min cycle):\n-----------------------\n`;
    out += `Token   | Action       | Score |\n`;
    out += `-------------------------------\n`;
    for (const sig of signals) {
        let scoreStr = sig.score > 80 ? `**${sig.score}%**` : `${sig.score}%`;
        let actionStr = sig.action.padEnd(12, ' ');
        let tokenStr = sig.symbol.padEnd(6, ' ');
        out += `${tokenStr}| ${actionStr}| ${scoreStr}\n`;
    }
    return out;
}

async function fetchDashboardData() {
    try {
        const res = await fetch('/api/dashboard-data');
        dashboardData = await res.json();
        document.getElementById('dashboard-content').textContent = formatDashboard(dashboardData);
    } catch (e) {
        document.getElementById('dashboard-content').textContent = 'Error loading dashboard.';
    }
}

function updateCountdown() {
    document.getElementById('countdown').textContent = `Refreshing in ${countdown}s`;
    countdown--;
    if (countdown < 0) countdown = refreshInterval;
}

// Initial fetch
fetchDashboardData();
setInterval(fetchDashboardData, apiInterval * 1000);
setInterval(() => {
    updateCountdown();
    if (countdown === 0) {
        fetchDashboardData();
    }
}, 1000);
