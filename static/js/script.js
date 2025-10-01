// Main JavaScript for Agentic Bot UI

// API Base URL
const API_BASE = '';

// DOM Elements
let chatMessagesContainer;

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    chatMessagesContainer = document.getElementById('chat-messages-container') || 
                           document.getElementById('chat-messages');
    
    // Set up event listeners
    const chatForm = document.getElementById('chat-form');
    if (chatForm) {
        chatForm.addEventListener('submit', handleChatSubmit);
    }

    // Load initial data if on main page
    if (window.location.pathname === '/') {
        loadDataSummary();
        loadChatHistory();
    }
}

// Handle chat form submission
async function handleChatSubmit(event) {
    event.preventDefault();
    
    const userInput = document.getElementById('user-input') || document.getElementById('user-query');
    const query = userInput.value.trim();
    
    if (!query) return;
    
    // Add user message to chat
    addChatMessage(query, 'user');
    userInput.value = '';
    
    // Show loading indicator
    const loadingId = addChatMessage('Thinking...', 'bot', true);
    
    try {
        // Send query to backend
        const response = await fetch('/query', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                query: query,
                user_id: 'web_user'
            })
        });
        
        const data = await response.json();
        
        // Remove loading message
        removeMessage(loadingId);
        
        // Add bot response
        addChatMessage(data.response, 'bot', false, data.operation_type, data.requires_approval, data.query_results);
        
        // Update approval badge if needed
        updateApprovalBadge();
        
        // Reload data summary
        if (window.location.pathname === '/') {
            loadDataSummary();
        }
        
    } catch (error) {
        removeMessage(loadingId);
        addChatMessage('Sorry, I encountered an error. Please try again.', 'bot');
        console.error('Error:', error);
    }
}

// Add message to chat
function addChatMessage(message, sender, isLoading = false, operationType = null, requiresApproval = false, queryResults = null) {
    if (!chatMessagesContainer) return null;
    
    const messageId = 'msg-' + Date.now();
    const messageDiv = document.createElement('div');
    messageDiv.id = messageId;
    messageDiv.className = `chat-message ${sender}-message`;
    
    if (operationType) {
        messageDiv.classList.add(`operation-${operationType}`);
    }
    
    if (requiresApproval) {
        messageDiv.classList.add('approval-required');
    }
    
    if (isLoading) {
        messageDiv.innerHTML = `
            <div class="d-flex align-items-center">
                <div class="spinner-border spinner-border-sm me-2" role="status"></div>
                <small class="text-muted">${message}</small>
            </div>
        `;
    } else {
        let messageContent = `<div class="message-content">${escapeHtml(message)}</div>`;
        
        // Add operation badge
        if (operationType) {
            const badgeClass = getBadgeClass(operationType);
            const badgeText = operationType.charAt(0).toUpperCase() + operationType.slice(1);
            messageContent = `
                <div class="d-flex justify-content-between align-items-start mb-1">
                    <span class="badge ${badgeClass}">${badgeText}</span>
                    ${requiresApproval ? '<span class="badge bg-warning text-dark"><i class="fas fa-clock me-1"></i>Approval Required</span>' : ''}
                </div>
                ${messageContent}
            `;
        }
        
        // Add query results if available
        if (queryResults && queryResults.length > 0) {
            messageContent += renderResultsTable(queryResults);
        }
        
        // Add approval buttons if approval required
        if (requiresApproval) {
            const requestId = extractRequestId(message);
            if (requestId) {
                messageContent += `
                    <div class="approval-actions mt-2">
                        <button class="btn btn-success btn-sm" onclick="handleApproval('${requestId}', true)">
                            <i class="fas fa-check me-1"></i>Approve
                        </button>
                        <button class="btn btn-danger btn-sm" onclick="handleApproval('${requestId}', false)">
                            <i class="fas fa-times me-1"></i>Reject
                        </button>
                    </div>
                `;
            }
        }
        
        messageDiv.innerHTML = messageContent;
    }
    
    chatMessagesContainer.appendChild(messageDiv);
    chatMessagesContainer.scrollTop = chatMessagesContainer.scrollHeight;
    
    return messageId;
}

// Remove message from chat
function removeMessage(messageId) {
    const messageElement = document.getElementById(messageId);
    if (messageElement) {
        messageElement.remove();
    }
}

// Handle approval actions
async function handleApproval(requestId, approved) {
    try {
        const response = await fetch('/approve', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                request_id: requestId,
                user_id: 'web_user',
                approved: approved
            })
        });
        
        const data = await response.json();
        
        // Show approval result
        addChatMessage(data.message, 'bot', false, 'read');
        
        // Update UI
        updateApprovalBadge();
        
        // Reload data if on main page
        if (window.location.pathname === '/') {
            loadDataSummary();
        }
        
        // Reload approvals page if active
        if (window.location.pathname === '/approvals') {
            loadPendingApprovals();
        }
        
    } catch (error) {
        addChatMessage('Error processing approval. Please try again.', 'bot');
        console.error('Error:', error);
    }
}

// Load pending approvals
async function loadPendingApprovals() {
    const container = document.getElementById('approvals-container');
    if (!container) return;
    
    try {
        const response = await fetch('/pending-approvals');
        const data = await response.json();
        
        const approvals = data.pending_approvals;
        
        if (Object.keys(approvals).length === 0) {
            container.innerHTML = `
                <div class="text-center py-4">
                    <i class="fas fa-check-circle fa-3x text-success mb-3"></i>
                    <h5>No Pending Approvals</h5>
                    <p class="text-muted">All operations have been processed.</p>
                </div>
            `;
            return;
        }
        
        let html = '';
        for (const [requestId, approval] of Object.entries(approvals)) {
            html += `
                <div class="approval-item">
                    <div class="d-flex justify-content-between align-items-start">
                        <div>
                            <h6>${approval.operation.toUpperCase()} Operation</h6>
                            <p class="mb-1"><strong>Query:</strong> ${approval.query}</p>
                            <small class="text-muted">Request ID: ${requestId}</small>
                        </div>
                        <div class="approval-actions">
                            <button class="btn btn-success btn-sm" onclick="handleApproval('${requestId}', true)">
                                <i class="fas fa-check me-1"></i>Approve
                            </button>
                            <button class="btn btn-danger btn-sm" onclick="handleApproval('${requestId}', false)">
                                <i class="fas fa-times me-1"></i>Reject
                            </button>
                        </div>
                    </div>
                </div>
            `;
        }
        
        container.innerHTML = html;
        
    } catch (error) {
        container.innerHTML = `
            <div class="alert alert-danger">
                <i class="fas fa-exclamation-triangle me-2"></i>
                Error loading approvals: ${error.message}
            </div>
        `;
    }
}

// Load data summary
async function loadDataSummary() {
    try {
        const [usersResponse, projectsResponse] = await Promise.all([
            fetch('/data/users'),
            fetch('/data/projects')
        ]);
        
        const usersData = await usersResponse.json();
        const projectsData = await projectsResponse.json();
        
        // Update users summary
        const usersSummary = document.getElementById('users-summary');
        if (usersSummary) {
            usersSummary.innerHTML = `
                <div class="d-flex justify-content-between">
                    <span>Total Users:</span>
                    <strong>${usersData.users.length}</strong>
                </div>
                <div class="mt-2">
                    <small class="text-muted">Departments:</small>
                    ${getDepartmentSummary(usersData.users)}
                </div>
            `;
        }
        
        // Update projects summary
        const projectsSummary = document.getElementById('projects-summary');
        if (projectsSummary) {
            projectsSummary.innerHTML = `
                <div class="d-flex justify-content-between">
                    <span>Total Projects:</span>
                    <strong>${projectsData.projects.length}</strong>
                </div>
                <div class="mt-2">
                    <small class="text-muted">Status:</small>
                    ${getProjectStatusSummary(projectsData.projects)}
                </div>
            `;
        }
        
    } catch (error) {
        console.error('Error loading data summary:', error);
    }
}

// Load chat history (for demo, we'll start fresh each time)
function loadChatHistory() {
    // In a real app, you might load previous chat history from localStorage or backend
    addChatMessage(
        "Hello! I'm your Agentic Bot. I can help you manage users and projects. Try asking me to show users or create a new project!", 
        'bot'
    );
}

// Update approval badge
async function updateApprovalBadge() {
    const badge = document.getElementById('approval-badge');
    if (!badge) return;
    
    try {
        const response = await fetch('/pending-approvals');
        const data = await response.json();
        const pendingCount = Object.keys(data.pending_approvals).length;
        
        if (pendingCount > 0) {
            badge.style.display = 'inline-block';
            badge.textContent = `${pendingCount} Approval${pendingCount > 1 ? 's' : ''} Required`;
        } else {
            badge.style.display = 'none';
        }
    } catch (error) {
        console.error('Error updating approval badge:', error);
    }
}

// Utility functions
function escapeHtml(unsafe) {
    return unsafe
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function getBadgeClass(operationType) {
    const classes = {
        'read': 'bg-success',
        'create': 'bg-primary',
        'update': 'bg-warning text-dark',
        'delete': 'bg-danger'
    };
    return classes[operationType] || 'bg-secondary';
}

function extractRequestId(message) {
    const match = message.match(/Request ID: ([a-f0-9-]+)/i);
    return match ? match[1] : null;
}

function renderResultsTable(results) {
    if (!results || results.length === 0) return '';
    
    // Handle both string results and object results
    const data = typeof results[0] === 'string' ? 
        results.map(r => ({ result: r })) : results;
    
    const headers = Object.keys(data[0] || {});
    
    return `
        <div class="mt-3">
            <div class="table-responsive">
                <table class="table table-sm table-bordered data-table">
                    <thead class="table-light">
                        <tr>
                            ${headers.map(header => `<th>${header}</th>`).join('')}
                        </tr>
                    </thead>
                    <tbody>
                        ${data.map(row => `
                            <tr>
                                ${headers.map(header => `<td>${row[header]}</td>`).join('')}
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        </div>
    `;
}

function getDepartmentSummary(users) {
    const deptCount = {};
    users.forEach(user => {
        deptCount[user.department] = (deptCount[user.department] || 0) + 1;
    });
    
    return Object.entries(deptCount)
        .map(([dept, count]) => `<span class="badge bg-light text-dark me-1">${dept}: ${count}</span>`)
        .join('');
}

function getProjectStatusSummary(projects) {
    const statusCount = {};
    projects.forEach(project => {
        statusCount[project.status] = (statusCount[project.status] || 0) + 1;
    });
    
    return Object.entries(statusCount)
        .map(([status, count]) => `<span class="badge bg-light text-dark me-1">${status}: ${count}</span>`)
        .join('');
}