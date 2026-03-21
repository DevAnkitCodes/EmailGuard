let riskChart, compositionChart;

async function updateDashboard() {
    const listContainer = document.getElementById('email-list');
    const statusPill = document.getElementById('status-pill');
    
    statusPill.innerText = "Scanning...";
    listContainer.innerHTML = '<p style="text-align:center; padding:20px;">Analyzing Inbox with AI...</p>';

    try {
        const response = await fetch('/scan-inbox');
        const data = await response.json();

        if (data.error) {
            listContainer.innerHTML = `<p style="color:var(--danger)">Error: ${data.error}. Please log in.</p>`;
            statusPill.innerText = "Error";
            return;
        }

        renderCharts(data);
        renderList(data);
        statusPill.innerText = "Analysis Complete";

    } catch (err) {
        console.error("Dashboard Update Failed:", err);
        statusPill.innerText = "Server Unreachable";
    }
}

function renderCharts(data) {
    const avgRisk = data.length > 0 ? (data.reduce((sum, e) => sum + e.score, 0) / data.length) * 100 : 0;
    const phishingCount = data.filter(e => e.status === 'phishing').length;
    const safeCount = data.filter(e => e.status === 'safe').length;

    // Update Text Label
    document.getElementById('risk-value').innerText = `${Math.round(avgRisk)}%`;

    // 1. Risk Meter (Gauge)
    const ctx1 = document.getElementById('riskMeter').getContext('2d');
    if (riskChart) riskChart.destroy();
    riskChart = new Chart(ctx1, {
        type: 'doughnut',
        data: {
            datasets: [{
                data: [avgRisk, 100 - avgRisk],
                backgroundColor: [avgRisk > 50 ? '#f85149' : '#58a6ff', '#21262d'],
                borderWidth: 0,
                circumference: 180,
                rotation: 270,
                cutout: '85%'
            }]
        },
        options: { plugins: { tooltip: { enabled: false } }, maintainAspectRatio: false }
    });

    // 2. Composition Chart (Pie)
    const ctx2 = document.getElementById('compositionChart').getContext('2d');
    if (compositionChart) compositionChart.destroy();
    compositionChart = new Chart(ctx2, {
        type: 'pie',
        data: {
            labels: ['Safe', 'Phishing'],
            datasets: [{
                data: [safeCount, phishingCount],
                backgroundColor: ['#3fb950', '#f85149'],
                borderColor: '#161b22',
                borderWidth: 2
            }]
        },
        options: { 
            plugins: { 
                legend: { position: 'bottom', labels: { color: '#c9d1d9', padding: 20 } } 
            },
            maintainAspectRatio: false 
        }
    });
}

function renderList(data) {
    const listContainer = document.getElementById('email-list');
    if (data.length === 0) {
        listContainer.innerHTML = '<p>No emails found.</p>';
        return;
    }

    listContainer.innerHTML = data.map(email => `
        <div class="email-item" style="border-left-color: ${email.status === 'safe' ? '#3fb950' : '#f85149'}">
            <div class="email-info">
                <div style="font-weight:600; color:white">${email.subject}</div>
                <div style="font-size:0.8rem; color:#8b949e">${email.explanation}</div>
            </div>
            <div class="email-meta" style="text-align:right">
                <div style="font-weight:bold; color:${email.status === 'safe' ? '#3fb950' : '#f85149'}">
                    ${Math.round(email.score * 100)}% Risk
                </div>
            </div>
        </div>
    `).join('');
}

document.getElementById('refresh-btn').addEventListener('click', updateDashboard);
window.onload = updateDashboard;
