function injectGuardButton() {
    // Gmail's top toolbar container
    const toolbar = document.querySelector('.G-atb'); 
    
    if (toolbar && !document.getElementById('guard-ai-btn')) {
        const btn = document.createElement('div');
        btn.id = 'guard-ai-btn';
        btn.innerHTML = '🛡️ Analyze Email';
        // Styling to match your glassmorphism theme
        btn.style = `
            background: linear-gradient(135deg, #3b82f6, #06b6d4);
            color: white;
            padding: 6px 14px;
            border-radius: 6px;
            margin-left: 15px;
            cursor: pointer;
            font-weight: bold;
            font-size: 12px;
            display: inline-block;
            vertical-align: middle;
            box-shadow: 0 4px 10px rgba(59, 130, 246, 0.3);
        `;
        
        btn.onclick = () => {
            const bodyText = document.querySelector('.a3s.aiL')?.innerText || "";
            const subjectText = document.querySelector('.hP')?.innerText || "No Subject";
            
            if (!bodyText) {
                alert("Please open an email first!");
                return;
            }

            // Redirects to your dashboard and passes the email data via URL parameters
            const dashboardUrl = `https://emailguard-ai.onrender.com/dashboard?scan=true&sub=${encodeURIComponent(subjectText)}&body=${encodeURIComponent(bodyText)}`;
            window.open(dashboardUrl, '_blank');
        };
        
        toolbar.appendChild(btn);
    }
}

// Gmail uses AJAX to load emails, so we check for the toolbar every 2 seconds
setInterval(injectGuardButton, 2000);
