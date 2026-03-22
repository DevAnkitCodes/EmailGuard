let riskMeter, compositionChart;

// 1. Function to handle the SINGLE email scan from the extension
async function runDeepAnalysis(content, subject) {
    const diveCard = document.getElementById('deep-dive-card');
    diveCard.style.display = 'block';
    window.scrollTo({ top: 0, behavior: 'smooth' });

    document.getElementById('dive-subject').innerText = subject;
    document.getElementById('dive-explanation').innerText = "AI is investigating content...";

    try {
        const response = await fetch('/analyze-single', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ content: content, subject: subject })
        });
        const result = await response.json();

        // Update the Deep Dive UI
        document.getElementById('dive-score').innerText = `${Math.round(result.score)}%`;
        document.getElementById('dive-verdict').innerText = result.verdict.toUpperCase();
        document.getElementById('dive-explanation').innerText = result.explanation;
        
        // Change color based on threat level
        const scoreColor = result.score > 50 ? '#ef4444' : '#3b82f6';
        document.getElementById('dive-score').style.color = scoreColor;

    } catch (err) {
        document.getElementById('dive-explanation').innerText = "Error connecting to AI server.";
    }
}

// 2. Function to load the GENERAL inbox status
async function refreshDashboard() {
    const listContainer = document.getElementById('email-list');
    listContainer.innerHTML = '<p style="color:#94a3b8; text-align:center;">Scanning latest threads...</p>';

    try {
        const response = await fetch('/scan-inbox');
        const data = await response.json();

        if (data.error) {
            listContainer.innerHTML = `<p style="color:#ef4444">Session expired. Please log in.</p>`;
            return;
        }

        renderVisuals(data);
    } catch (err) {
        listContainer.innerHTML = `<p style="color:#ef4444">Server is offline or waking up...</p>`;
    }
}

function renderVisuals(data) {
    const totalRisk = data.length > 0 ? (data.reduce((s, e) => s + e.score, 0) / data.length) : 0;
    const safeCount = data.filter(e => e.status === 'safe').length;
    const threatCount = data.length - safeCount;

    document.getElementById('risk-text').innerText = `${Math.round(totalRisk)}%`;

    // Risk Meter (Gauge)
    const ctx1 = document.getElementById('riskMeter').getContext('2d');
    if (riskMeter) riskMeter.destroy();
    riskMeter = new Chart(ctx1, {
        type: 'doughnut',
        data: {
            datasets: [{
                data: [totalRisk, 100 - totalRisk],
                backgroundColor: [totalRisk > 50 ? '#ef4444' : '#3b82f6', '#1e293b'],
                circumference: 180,
                rotation: 270,
                cutout: '85%',
                borderWidth: 0
            }]
        },
        options: { plugins: { tooltip: { enabled: false } }, maintainAspectRatio: false }
    });

    // Composition (Pie)
    const ctx2 = document.getElementById('compChart').getContext('2d');
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
            plugins: { legend: { position: 'bottom', labels: { color: '#94a3b8' } } },
            maintainAspectRatio: false 
        }
    });

    // Email Log List
    document.getElementById('email-list').innerHTML = data.map(e => `
        <div class="email-item" style="border-left: 4px solid ${e.status === 'safe' ? '#10b981' : '#ef4444'}">
            <div>
                <strong>${e.subject}</strong>
                <small>${e.explanation}</small>
            </div>
            <div style="font-weight:bold; color:${e.status === 'safe' ? '#10b981' : '#ef4444'}">${e.score}%</div>
        </div>
    `).join('');
}

// 3. Initialize & Check for Extension parameters
window.onload = () => {
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('scan') === 'true') {
        runDeepAnalysis(urlParams.get('body'), urlParams.get('sub'));
    }
    refreshDashboard();
};

document.getElementById('refresh-btn').addEventListener('click', refreshDashboard);
