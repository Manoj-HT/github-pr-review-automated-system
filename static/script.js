document.getElementById('reviewForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const prUrl = document.getElementById('prUrlInput').value;
    const userMsg = document.getElementById('userMessageInput').value;
    if(!prUrl) return;

    // Add User Message
    addMessage(prUrl + (userMsg ? ` (Msg: ${userMsg})` : ''), 'user');
    
    // Clear inputs
    document.getElementById('prUrlInput').value = '';
    document.getElementById('userMessageInput').value = '';

    // Add Loading Message
    const loadingId = addLoadingMessage();

    try {
        const response = await fetch('/api/review', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ pr_url: prUrl, user_message: userMsg })
        });
        
        const data = await response.json();
        removeMessage(loadingId);
        
        if (data.error) {
            addMessage(`Error: ${data.error}`, 'system');
        } else {
            renderResults(data.results);
        }
    } catch (err) {
        removeMessage(loadingId);
        addMessage(`Network error occurred: ${err.message}`, 'system');
    }
});

function addMessage(text, sender) {
    const chatArea = document.getElementById('chatArea');
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${sender}-message`;
    
    const initial = sender === 'user' ? 'U' : 'S';
    
    msgDiv.innerHTML = `
        <div class="avatar">${initial}</div>
        <div class="bubble"><p>${text}</p></div>
    `;
    chatArea.appendChild(msgDiv);
    chatArea.scrollTop = chatArea.scrollHeight;
}

function addLoadingMessage() {
    const chatArea = document.getElementById('chatArea');
    const msgDiv = document.createElement('div');
    msgDiv.className = `message system-message`;
    const id = 'msg-' + Date.now();
    msgDiv.id = id;
    
    msgDiv.innerHTML = `
        <div class="avatar">S</div>
        <div class="bubble">
            <p>Analyzing Repository and PR...</p>
            <div class="loading-dots">
                <div class="dot"></div>
                <div class="dot"></div>
                <div class="dot"></div>
            </div>
        </div>
    `;
    chatArea.appendChild(msgDiv);
    chatArea.scrollTop = chatArea.scrollHeight;
    return id;
}

function removeMessage(id) {
    const el = document.getElementById(id);
    if(el) el.remove();
}

function renderResults(results) {
    const chatArea = document.getElementById('chatArea');
    const msgDiv = document.createElement('div');
    msgDiv.className = `message system-message`;
    
    let htmlContent = `<div class="avatar">S</div><div class="bubble"><p>Analysis Complete! Here are the findings:</p>`;
    
    if (results.message) {
        htmlContent += `<p><em>${results.message}</em></p>`;
    } else {
        for (const [check, data] of Object.entries(results)) {
            const passedInfo = data.passed;
            const rating = data.rating || "N/A";
            const isPass = passedInfo === true;
            
            htmlContent += `
                <div class="review-card">
                    <div class="review-header">
                        <span class="review-title">${check} (Rating: ${rating}/10)</span>
                        <span class="badge ${isPass ? 'pass' : 'fail'}">${isPass ? 'PASSED' : 'FAILED'}</span>
                    </div>
            `;
            
            if (data.issues && data.issues.length > 0) {
                data.issues.forEach(issue => {
                    htmlContent += `
                        <div class="issue-item">
                            <div><strong>File:</strong> ${issue.file || 'General'}</div>
                            <div><strong>Reason:</strong> ${issue.reason}</div>
                            <div style="margin-top:4px; color:#58a6ff;"><strong>Fix:</strong> ${issue.fix}</div>
                        </div>
                    `;
                });
            } else {
                htmlContent += `<div class="issue-item">No major issues found.</div>`;
            }
            htmlContent += `</div>`;
        }
    }
    
    htmlContent += `</div>`;
    msgDiv.innerHTML = htmlContent;
    chatArea.appendChild(msgDiv);
    chatArea.scrollTop = chatArea.scrollHeight;
}
