let riskChart, compChart;

async function fetchData() {
    const listContainer = document.getElementById('email-list');
    listContainer.innerHTML = '<p class="loading-text">Scanning your inbox...</p>';

    try {
        const response = await fetch('/scan-inbox');
        const data = await response.json();

        if (data.error) {
            listContainer.innerHTML = '<p style="color:red">Unauthorized. Please login again.</p>';
            return;
        }

        updateDashboard(data);
    } catch (err) {
        console.error("Fetch Error:", err);
    }
}

function updateDashboard(data) {
    const safeEmails = data.filter(e => e.status === 'safe');
    const threatEmails = data.filter(e => e.status === 'phishing');
    
    // 1. Calculate Average Risk Score (0-100)
    const avgScore = data.length > 0 
        ? Math.round(data.reduce((sum, e) => sum + (e.score * 100), 0) / data.length) 
        : 0;

    document.getElementById('risk-label').innerText = `${avgScore}%`;
    document.getElementById('scan-count').innerText = `${data.length} Emails Scanned`;

    // 2. Risk Meter (Gauge Chart)
    const riskCtx = document.getElementById('riskMeter').getContext('2d');
    if (riskChart) riskChart.destroy();
    riskChart = new Chart(riskCtx, {
        type: 'doughnut',
        data: {
            datasets: [{
                data: [avgScore, 100 - avgScore],
                backgroundColor: [avgScore > 50 ? '#f43f5e' : '#22d3ee', '#334155'],
                borderWidth: 0,
                circumference: 180,
                rotation: 270,
                cutout: '80%'
            }]
        },
        options: { plugins: { tooltip: { enabled: false } } }
    });

    // 3. Composition Chart
    const compCtx = document.getElementById('compositionChart').getContext('2d');
    if (compChart) compChart.destroy();
    compChart = new Chart(compCtx, {
        type: 'pie',
        data: {
            labels: ['Safe', 'Phishing'],
            datasets: [{
                data: [safeEmails.length, threatEmails.length],
                backgroundColor: ['#10b981', '#f43f5e'],
                borderColor: '#1e293b'
            }]
        },
        options: { plugins: { legend: { position: 'bottom', labels: { color: '#fff' } } } }
    });

    // 4. Update Email List
    const emailList = document.getElementById('email-list');
    emailList.innerHTML = data.map(email => `
        <div class="email-entry" style="border-left-color: ${email.status === 'safe' ? '#10b981' : '#f43f5e'}">
            <div>
                <div style="font-weight:bold">${email.subject}</div>
                <div style="font-size:0.8rem; color:#94a3b8">${email.explanation}</div>
            </div>
            <span class="badge ${email.status === 'safe' ? 'bg-safe' : 'bg-danger'}">
                ${Math.round(email.score * 100)}% Risk
            </span>
        </div>
    `).join('');
}

document.getElementById('refresh-btn').addEventListener('click', fetchData);
window.onload = fetchData;
