/**
 * Cognitive Reframer - Frontend Application
 * Handles UI interactions and API communication
 */

// Configuration
const API_ENDPOINT = 'API_ENDPOINT_PLACEHOLDER'; // Will be replaced during deployment
const USER_ID = 'demo_user_' + Math.random().toString(36).substring(7); // Demo user ID

// State
let currentReframe = null;

// DOM Elements
const thoughtInput = document.getElementById('thought-input');
const charCount = document.getElementById('char-count');
const reframeBtn = document.getElementById('reframe-btn');
const toneSelect = document.getElementById('tone');
const resultsSection = document.getElementById('results-section');
const reframesContainer = document.getElementById('reframes-container');
const originalThoughtText = document.getElementById('original-thought-text');
const summaryText = document.getElementById('summary-text');
const safetyMessage = document.getElementById('safety-message');
const safetyMessageText = document.getElementById('safety-message-text');
const crisisResourcesList = document.getElementById('crisis-resources-list');
const saveBtn = document.getElementById('save-btn');
const scheduleBtn = document.getElementById('schedule-btn');
const newReframeBtn = document.getElementById('new-reframe-btn');
const historyContainer = document.getElementById('history-container');
const historyLoading = document.getElementById('history-loading');
const historyEmpty = document.getElementById('history-empty');

// Navigation
document.querySelectorAll('.nav-btn').forEach(btn => {
    btn.addEventListener('click', () => {
        const view = btn.dataset.view;
        switchView(view);
    });
});

function switchView(view) {
    // Update nav buttons
    document.querySelectorAll('.nav-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.view === view);
    });

    // Update views
    document.querySelectorAll('.view').forEach(v => {
        v.classList.toggle('active', v.id === `${view}-view`);
    });

    // Load history if switching to history view
    if (view === 'history') {
        loadHistory();
    }
}

// Input handling
thoughtInput.addEventListener('input', () => {
    const length = thoughtInput.value.length;
    charCount.textContent = length;
    reframeBtn.disabled = length === 0;
});

// Reframe button
reframeBtn.addEventListener('click', async () => {
    const input = thoughtInput.value.trim();
    const tone = toneSelect.value;

    if (!input) return;

    setLoading(true);
    hideResults();
    hideSafety();

    try {
        const response = await fetch(`${API_ENDPOINT}/reframe`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                action: 'reframe',
                user_id: USER_ID,
                input: input,
                tone: tone
            })
        });

        const data = await response.json();

        if (data.safety_response) {
            showSafetyMessage(data);
        } else {
            currentReframe = data;
            displayReframes(data);
        }
    } catch (error) {
        console.error('Error:', error);
        showToast('Failed to generate reframes. Please try again.', 'error');
    } finally {
        setLoading(false);
    }
});

// Display reframes
function displayReframes(data) {
    originalThoughtText.textContent = data.input;
    summaryText.textContent = data.summary;

    reframesContainer.innerHTML = '';

    data.reframes.forEach((reframe, index) => {
        const card = document.createElement('div');
        card.className = 'reframe-card';
        card.innerHTML = `
            <div class="reframe-header">
                <div class="model-badge">${reframe.model}</div>
                <div class="reframe-number">${index + 1}</div>
            </div>
            <div class="reframe-content">
                <h4 class="reframe-text">"${reframe.reframe}"</h4>
                <p class="reframe-explanation">${reframe.explanation}</p>
                
                <div class="action-steps">
                    <strong>Action Steps:</strong>
                    <ol>
                        ${reframe.action_steps.map(step => `<li>${step}</li>`).join('')}
                    </ol>
                </div>
            </div>
        `;
        reframesContainer.appendChild(card);
    });

    resultsSection.style.display = 'block';
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// Safety message
function showSafetyMessage(data) {
    safetyMessageText.textContent = data.message;
    
    crisisResourcesList.innerHTML = '';
    data.resources.forEach(resource => {
        const li = document.createElement('li');
        li.textContent = resource;
        crisisResourcesList.appendChild(li);
    });

    safetyMessage.style.display = 'flex';
    safetyMessage.scrollIntoView({ behavior: 'smooth' });
}

function hideSafety() {
    safetyMessage.style.display = 'none';
}

// Save button
saveBtn.addEventListener('click', async () => {
    if (!currentReframe) return;

    try {
        showToast('Saved to memory! 💾', 'success');
        saveBtn.disabled = true;
        saveBtn.textContent = '✓ Saved';
    } catch (error) {
        console.error('Error saving:', error);
        showToast('Failed to save. Please try again.', 'error');
    }
});

// Schedule button
scheduleBtn.addEventListener('click', async () => {
    if (!currentReframe) return;

    const followUpHours = parseFollowUp(currentReframe.follow_up);
    const followUpDate = new Date(Date.now() + followUpHours * 60 * 60 * 1000);

    try {
        // In production, this would call the schedule API
        showToast(`Follow-up scheduled for ${followUpDate.toLocaleString()} 📅`, 'success');
        scheduleBtn.disabled = true;
        scheduleBtn.textContent = '✓ Scheduled';
    } catch (error) {
        console.error('Error scheduling:', error);
        showToast('Failed to schedule. Please try again.', 'error');
    }
});

// New reframe button
newReframeBtn.addEventListener('click', () => {
    hideResults();
    thoughtInput.value = '';
    thoughtInput.focus();
    charCount.textContent = '0';
    reframeBtn.disabled = true;
    currentReframe = null;
});

// Load history
async function loadHistory() {
    historyLoading.style.display = 'flex';
    historyContainer.innerHTML = '';
    historyEmpty.style.display = 'none';

    try {
        const response = await fetch(`${API_ENDPOINT}/history`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                action: 'history',
                user_id: USER_ID
            })
        });

        const data = await response.json();

        historyLoading.style.display = 'none';

        if (!data.history || data.history.length === 0) {
            historyEmpty.style.display = 'block';
            return;
        }

        data.history.forEach(item => {
            const card = createHistoryCard(item);
            historyContainer.appendChild(card);
        });

    } catch (error) {
        console.error('Error loading history:', error);
        historyLoading.style.display = 'none';
        showToast('Failed to load history. Please try again.', 'error');
    }
}

function createHistoryCard(item) {
    const card = document.createElement('div');
    card.className = 'history-card';
    
    const date = new Date(item.created_at);
    const dateStr = date.toLocaleDateString('en-US', { 
        month: 'short', 
        day: 'numeric',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });

    card.innerHTML = `
        <div class="history-header">
            <span class="history-date">${dateStr}</span>
            <div class="history-models">
                ${(item.models_used || []).map(model => 
                    `<span class="model-badge">${model}</span>`
                ).join('')}
            </div>
        </div>
        <div class="history-content">
            <p class="history-input">"${item.source_input}"</p>
            <p class="history-summary">${item.summary}</p>
        </div>
        <button class="btn btn-text" onclick="viewHistoryDetails('${item.reframe_id}')">
            View Details →
        </button>
    `;

    return card;
}

function viewHistoryDetails(reframeId) {
    // In production, fetch full details and display in modal
    showToast('Opening details... (feature coming soon)', 'info');
}

// Utility functions
function setLoading(loading) {
    const btnText = reframeBtn.querySelector('.btn-text');
    const btnLoader = reframeBtn.querySelector('.btn-loader');
    
    if (loading) {
        btnText.style.display = 'none';
        btnLoader.style.display = 'inline-block';
        reframeBtn.disabled = true;
    } else {
        btnText.style.display = 'inline';
        btnLoader.style.display = 'none';
        reframeBtn.disabled = false;
    }
}

function hideResults() {
    resultsSection.style.display = 'none';
    saveBtn.disabled = false;
    saveBtn.textContent = '💾 Save to Memory';
    scheduleBtn.disabled = false;
    scheduleBtn.textContent = '📅 Schedule Follow-up';
}

function parseFollowUp(followUpStr) {
    try {
        const parts = followUpStr.toLowerCase().split(' ');
        if (followUpStr.includes('hour')) {
            return parseInt(parts[0]);
        } else if (followUpStr.includes('day')) {
            return parseInt(parts[0]) * 24;
        }
    } catch (e) {
        console.error('Error parsing follow_up:', e);
    }
    return 48; // default
}

function showToast(message, type = 'info') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast toast-${type} show`;
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    console.log('Cognitive Reframer initialized');
    console.log('API Endpoint:', API_ENDPOINT);
    console.log('User ID:', USER_ID);
});

