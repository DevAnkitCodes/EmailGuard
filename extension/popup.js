const RENDER_URL = "https://emailguard-ai.onrender.com";

document.getElementById('scan-btn').addEventListener('click', async () => {
    const status = document.getElementById('status');
    status.innerText = "Scanning...";

    try {
        const response = await fetch(`${RENDER_URL}/scan-inbox`, {
            credentials: 'include' // CRITICAL for session sharing
        });
        
        const data = await response.json();
        
        if (data.error) {
            status.innerText = "Error: Login on Dashboard first.";
        } else {
            status.innerText = `Success! ${data.length} emails scanned.`;
        }
    } catch (e) {
        status.innerText = "Server Unreachable.";
    }
});
