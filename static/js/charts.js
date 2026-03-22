let riskMeter, healthChart;

// 1. Function to handle the SINGLE email scan from the Extension
async function runDeepAnalysis(content, subject) {
    const diveCard = document.getElementById('deep-dive-card');
    diveCard.style.display = 'block'; // Reveal the hidden box
    window.scrollTo({ top: 0, behavior: 'smooth' });

    document.getElementById('dive-subject').innerText = subject;
    document.getElementById('dive-explanation').innerText = "AI is investigating the content...";

    try {
        const response = await fetch('/analyze-single', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ content: content, subject: subject })
        });
        const result = await response.json();

        // Update the Deep Dive UI with AI results
        document.getElementById('dive-score').innerText = `${result.score}%`;
        document.getElementById('dive-verdict').innerText = result.verdict.toUpperCase();
        document.getElementById('dive-explanation').innerText = result.explanation;
        
        // UI Polish: Change score color based on danger
        document.getElementById('dive-score').style.color = result.score > 50 ? '#ef4444' : '#3b82f6';

    } catch (err) {
        document.getElementById('dive-explanation').innerText = "Failed to connect to AI backend.";
    }
}

// 2. Function to load the Dashboard Data (Risk Meter + Log)
async function refreshDashboard() {
    try {
        const response = await fetch('/scan-inbox');
        const data = await response.json();
        
        updateCharts(data);
    } catch (err) {
        console.error("Dashboard sync failed:", err);
    }
}

function updateCharts(data) {
    const avgRisk = data.reduce((s, e) => s + e.score, 0) / data.length;
    
    // Update the center text of the Gauge
    document.getElementById('risk-text').innerText = `${Math.round(avgRisk)}%`;

    // Global Risk Meter
    const ctx1 = document.getElementById('riskMeter').getContext('2d');
    if (riskMeter) riskMeter.destroy();
    riskMeter = new Chart(ctx1, {
        type: 'doughnut',
        data: {
            datasets: [{
                data: [avgRisk, 100 - avgRisk],
                backgroundColor: [avgRisk > 50 ? '#ef4444' : '#3b82f6', '#1e293b'],
                circumference: 180,
                rotation: 270,
                cutout: '85%',
                borderWidth: 0
            }]
        },
        options: { plugins: { tooltip: { enabled: false } }, maintainAspectRatio: false }
    });

    // Threat Analysis Log (The List)
    document.getElementById('email-list').innerHTML = data.map(e => `
        <div class="email-item" style="border-left: 4px solid ${e.score > 50 ? '#ef4444' : '#10b981'}">
            <div>
                <strong>${e.subject}</strong>
                <small>${e.explanation}</small>
            </div>
            <div style="font-weight:bold; color:${e.score > 50 ? '#ef4444' : '#10b981'}">${e.score}%</div>
        </div>
    `).join('');
}

// 3. Page Initialization Logic
window.onload = () => {
    const urlParams = new URLSearchParams(window.location.search);
    
    // If we arrived here from the Gmail "Analyze" button
    if (urlParams.get('scan') === 'true') {
        runDeepAnalysis(urlParams.get('body'), urlParams.get('sub'));
    }
    
    refreshDashboard();
};

document.getElementById('refresh-btn').addEventListener('click', refreshDashboard);
