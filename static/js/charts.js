document.addEventListener('DOMContentLoaded', function() {
    const ctx = document.getElementById('riskChart').getContext('2d');
    let riskChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Safe', 'Suspicious', 'Dangerous'],
            datasets: [{
                data: [0, 0, 0],
                backgroundColor: ['#10b981', '#f59e0b', '#ef4444'],
                borderWidth: 0
            }]
        },
        options: { cutout: '80%', plugins: { legend: { display: false } } }
    });

    async function runScan() {
        const list = document.getElementById('report-list');
        list.innerHTML = "<div class='p-10 text-center text-blue-400 animate-pulse'>ANALYZING INBOX...</div>";

        try {
            const res = await fetch("/scan-inbox", { credentials: 'include' });
            if (!res.ok) throw new Error("Please Login via Google");

            const data = await res.json();
            list.innerHTML = "";
            let counts = { safe: 0, suspicious: 0, dangerous: 0 };

            data.forEach(item => {
                counts[item.status]++;
                const color = item.status === 'dangerous' ? 'red' : (item.status === 'suspicious' ? 'yellow' : 'green');
                list.innerHTML += `
                    <div class="p-4 bg-slate-900 rounded-xl border-l-4 border-${color}-500 shadow-xl">
                        <h3 class="font-bold text-sm">${item.subject}</h3>
                        <p class="text-blue-300 text-xs mt-1">AI: ${item.explanation}</p>
                    </div>`;
            });

            riskChart.data.datasets[0].data = [counts.safe, counts.suspicious, counts.dangerous];
            riskChart.update();
        } catch (e) {
            list.innerHTML = `<div class='text-red-500 text-center'>${e.message}</div>`;
        }
    }

    document.getElementById('fetchData').onclick = runScan;
    runScan();
});