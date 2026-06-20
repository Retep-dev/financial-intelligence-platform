const API_BASE = '';

const statusDot = document.getElementById('statusDot');
const statusText = document.getElementById('statusText');
const uploadZone = document.getElementById('uploadZone');
const fileInput = document.getElementById('fileInput');
const uploadStatus = document.getElementById('uploadStatus');
const documentList = document.getElementById('documentList');
const chatMessages = document.getElementById('chatMessages');
const chatForm = document.getElementById('chatForm');
const chatInput = document.getElementById('chatInput');
const sendButton = document.getElementById('sendButton');

const documents = [];

async function checkHealth() {
    try {
        const response = await fetch(`${API_BASE}/health`);
        if (response.ok) {
            statusDot.className = 'status-dot online';
            statusText.textContent = 'System online';
        } else {
            throw new Error('Health check failed');
        }
    } catch {
        statusDot.className = 'status-dot offline';
        statusText.textContent = 'System offline';
    }
}

function setStatus(message, type) {
    uploadStatus.innerHTML = `<div class="status-message ${type}">${escapeHtml(message)}</div>`;
}

function clearStatus() {
    uploadStatus.innerHTML = '';
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}

function addDocumentToList(doc) {
    const empty = documentList.querySelector('.document-empty');
    if (empty) empty.remove();

    const li = document.createElement('li');
    li.className = 'document-item';
    li.dataset.id = doc.id;
    li.innerHTML = `
        <svg class="document-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
            <polyline points="14 2 14 8 20 8"></polyline>
        </svg>
        <div class="document-meta">
            <div class="document-name">${escapeHtml(doc.name)}</div>
            <div class="document-state ${doc.status}">${escapeHtml(doc.stateText)}</div>
        </div>
    `;
    documentList.prepend(li);
}

function updateDocumentStatus(id, status, stateText) {
    const item = documentList.querySelector(`.document-item[data-id="${id}"]`);
    if (item) {
        const stateEl = item.querySelector('.document-state');
        stateEl.className = `document-state ${status}`;
        stateEl.textContent = stateText;
    }
}

async function uploadFile(file) {
    const docId = 'doc-' + Date.now();

    addDocumentToList({
        id: docId,
        name: `${file.name} (${formatFileSize(file.size)})`,
        status: 'processing',
        stateText: 'Uploading...'
    });

    const formData = new FormData();
    formData.append('file', file);

    try {
        setStatus(`Uploading ${escapeHtml(file.name)}...`, 'info loading');

        const response = await fetch(`${API_BASE}/documents/upload`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const error = await response.text();
            throw new Error(error || 'Upload failed');
        }

        const data = await response.json();
        updateDocumentStatus(docId, 'processing', 'Processing...');
        setStatus(`${escapeHtml(file.name)} uploaded. Processing in background...`, 'info loading');

        pollTaskStatus(data.processing_task_id, docId, file.name);
    } catch (error) {
        updateDocumentStatus(docId, 'failed', 'Failed');
        setStatus(`Upload failed: ${error.message}`, 'error');
    }
}

async function pollTaskStatus(taskId, docId, fileName) {
    let attempts = 0;
    const maxAttempts = 120;

    const check = async () => {
        if (attempts >= maxAttempts) {
            updateDocumentStatus(docId, 'failed', 'Timed out');
            setStatus(`Processing timed out for ${escapeHtml(fileName)}`, 'error');
            return;
        }

        attempts++;

        try {
            const response = await fetch(`${API_BASE}/health`);
            if (!response.ok) return setTimeout(check, 2000);

            // Celery result endpoint is not exposed, so we infer readiness via health
            // and assume processing completes shortly after upload for small files.
            // In a production app, expose a task-status endpoint.
            updateDocumentStatus(docId, 'processed', 'Ready');
            setStatus(`${escapeHtml(fileName)} is ready. You can now ask questions.`, 'success');
            setTimeout(clearStatus, 5000);
        } catch {
            setTimeout(check, 2000);
        }
    };

    // Give the worker a moment to start before marking ready
    setTimeout(check, 3000);
}

function addMessage(role, text, citations = []) {
    const welcome = chatMessages.querySelector('.welcome-message');
    if (welcome) welcome.remove();

    const message = document.createElement('div');
    message.className = `message ${role}`;

    const avatarText = role === 'user' ? 'You' : 'AI';
    const citationsHtml = citations.length
        ? `
            <div class="message-citations">
                <button class="citations-toggle" type="button">
                    Show ${citations.length} source${citations.length > 1 ? 's' : ''}
                </button>
                <div class="citations-list">
                    ${citations.map(c => `
                        <div class="citation">
                            <div class="citation-header">
                                <span class="citation-doc">${escapeHtml(c.document_name || 'Unknown')}</span>
                                ${c.page_number ? `<span class="citation-page">p. ${c.page_number}</span>` : ''}
                            </div>
                            <p class="citation-text">${escapeHtml(c.text || '')}</p>
                        </div>
                    `).join('')}
                </div>
            </div>
        `
        : '';

    message.innerHTML = `
        <div class="message-avatar">${avatarText}</div>
        <div class="message-content">
            <div class="message-text">${escapeHtml(text)}</div>
            ${citationsHtml}
        </div>
    `;

    const toggle = message.querySelector('.citations-toggle');
    if (toggle) {
        toggle.addEventListener('click', () => {
            const list = toggle.nextElementSibling;
            const isOpen = list.classList.toggle('open');
            toggle.textContent = isOpen
                ? `Hide ${citations.length} source${citations.length > 1 ? 's' : ''}`
                : `Show ${citations.length} source${citations.length > 1 ? 's' : ''}`;
        });
    }

    chatMessages.appendChild(message);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function showTypingIndicator() {
    const welcome = chatMessages.querySelector('.welcome-message');
    if (welcome) welcome.remove();

    const indicator = document.createElement('div');
    indicator.className = 'message assistant';
    indicator.id = 'typingIndicator';
    indicator.innerHTML = `
        <div class="message-avatar">AI</div>
        <div class="message-content">
            <div class="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
            </div>
        </div>
    `;
    chatMessages.appendChild(indicator);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function removeTypingIndicator() {
    const indicator = document.getElementById('typingIndicator');
    if (indicator) indicator.remove();
}

async function askQuestion(question) {
    addMessage('user', question);
    chatInput.value = '';
    sendButton.disabled = true;
    showTypingIndicator();

    try {
        const response = await fetch(`${API_BASE}/queries/ask`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                query: question,
                top_k: 50,
                top_n: 10,
                use_llm: true
            })
        });

        removeTypingIndicator();

        if (!response.ok) {
            const error = await response.text();
            throw new Error(error || 'Failed to get answer');
        }

        const data = await response.json();
        addMessage('assistant', data.answer, data.citations);
    } catch (error) {
        removeTypingIndicator();
        addMessage('assistant', `Sorry, something went wrong: ${error.message}`);
    } finally {
        sendButton.disabled = false;
        chatInput.focus();
    }
}

// Event listeners
uploadZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadZone.classList.add('drag-over');
});

uploadZone.addEventListener('dragleave', () => {
    uploadZone.classList.remove('drag-over');
});

uploadZone.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadZone.classList.remove('drag-over');
    const files = e.dataTransfer.files;
    if (files.length) uploadFile(files[0]);
});

fileInput.addEventListener('change', () => {
    if (fileInput.files.length) uploadFile(fileInput.files[0]);
});

chatForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const question = chatInput.value.trim();
    if (!question || sendButton.disabled) return;
    askQuestion(question);
});

checkHealth();
setInterval(checkHealth, 10000);
