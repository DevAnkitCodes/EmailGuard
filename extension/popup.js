const RENDER_URL = "https://emailguard-ai.onrender.com";

document.getElementById('scan-btn').addEventListener('click', async () => {
    const status = document.getElementById('status');
    status.innerText = "Connecting...";

    try {
        // We MUST include credentials to share the login session
        const response = await fetch(`${RENDER_URL}/scan-inbox`, {
            credentials: 'include'
        });
        
        const data = await response.json();
        
        if (data.error) {
            status.innerText = "Login on Dashboard First.";
        } else {
            status.innerText = `Found ${data.length} emails. Check Dashboard!`;
            // Optional: Reload the dashboard tab if it's open
        }
    } catch (e) {
        status.innerText = "Server Unreachable.";
        console.error(e);
    }
});
