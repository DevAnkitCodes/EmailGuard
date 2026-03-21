const RENDER_URL = "https://your-app-name.onrender.com";

document.getElementById('scan-btn').addEventListener('click', async () => {
    const status = document.getElementById('status');
    status.innerText = "Connecting...";

    try {
        const response = await fetch(`${RENDER_URL}/scan-inbox`);
        const data = await response.json();
        
        if (data.error) {
            status.innerText = "Login on Dashboard First.";
        } else {
            status.innerText = `Found ${data.length} threads. Check Dashboard for AI insights.`;
        }
    } catch (e) {
        status.innerText = "Server Unreachable.";
    }
});