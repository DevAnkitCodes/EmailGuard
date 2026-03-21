let riskMeterChart, compositionChart;

async function runAnalysis() {
    const list = document.getElementById('email-list');
    const badge = document.getElementById('scan-count');
    list.innerHTML = '<p style="text-align:center; color: #94a3b8;">Scanning inbox for phishing threats...</p>';

    try {
        const response = await fetch('/scan-inbox');
        const data = await response.json();

        if (data.error) {
            list.innerHTML = `<p style="color:#ef4444">Error: ${data.error}</p>`;
            return;
        }

        badge.innerText = `${data.length} Scanned`;
        renderCharts(data);
        renderList(data);
    } catch (err) {
        console.error("Scan failed:", err);
    }
}

function renderCharts(data) {
    const avgRisk = data.length > 0 ? (data.reduce((s, e) => s + e.score, 0) / data.length) * 100 : 0;
    const safeCount = data.filter(e => e.status === 'safe').length;
    const threatCount = data.filter(e => e.status !== 'safe').length;

    document.getElementById('risk-display').innerText = `${Math.round(avgRisk)}%`;

    // 1. Gauge Chart
    const ctx1 = document.getElementById('riskMeter').getContext('2d');
    if (riskMeterChart) riskMeterChart.destroy();
    riskMeterChart = new Chart(ctx1, {
        type: 'doughnut',
        data: {
            datasets: [{
                data: [avgRisk, 100 - avgRisk],
                backgroundColor: [avgRisk > 50 ? '#ef4444' : '#3b82f6', '#1e293b'],
                borderWidth: 0, circumference: 180, rotation: 270, cutout: '85%'
            }]
        },
        options: { plugins: { tooltip: { enabled: false } }, maintainAspectRatio: false }
    });

    // 2. Pie Chart
    const ctx2 = document.getElementById('compositionChart').getContext('2d');
    if (compositionChart) compositionChart.destroy();
    compositionChart = new Chart(ctx2, {
        type: 'pie',
        data: {
            labels: ['Safe', 'Threats'],
            datasets: [{
                data: [safeCount, threatCount],
                backgroundColor: ['#10b981', '#ef4444'],
                borderWidth: 0
            }]
        },
        options: { 
            plugins: { legend: { position: 'bottom', labels: { color: '#94a3b8', font: { size: 12 } } } },
            maintainAspectRatio: false
        }
    });
}

function renderList(data) {
    const list = document.getElementById('email-list');
    list.innerHTML = data.map(email => `
        <div class="email-row" style="border-left-color: ${email.status === 'safe' ? '#10b981' : '#ef4444'}">
            <div class="email-info">
                <h4>${email.subject}</h4>
                <p>${email.explanation}</p>
            </div>
            <div class="score-badge ${email.status === 'safe' ? 'safe' : 'threat'}">
                ${Math.round(email.score * 100)}%
            </div>
        </div>
    `).join('');
}

document.getElementById('refresh-btn').addEventListener('click', runAnalysis);
window.onload = runAnalysis;
