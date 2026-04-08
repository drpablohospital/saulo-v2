/**
 * Saulo v2 - Simple chat interface
 * WhatsApp-like experience with Ollama backend
 */

// State
let currentConversationId = null;
let isLangostaMode = false;
let authToken = localStorage.getItem('saulo_token');
let availableModels = [];

// DOM Elements
const elements = {
    messagesContainer: document.getElementById('messages-container'),
    messageInput: document.getElementById('message-input'),
    sendBtn: document.getElementById('send-btn'),
    modelSelect: document.getElementById('model-select'),
    conversationsList: document.getElementById('conversations-list'),
    newChatBtn: document.getElementById('new-chat-btn'),
    adminBtn: document.getElementById('admin-btn'),
    loginModal: document.getElementById('login-modal'),
    langostaBadge: document.getElementById('langosta-badge'),
    menuToggle: document.getElementById('menu-toggle'),
    sidebar: document.getElementById('sidebar'),
    chatContainer: document.querySelector('.chat-container'),
    usernameInput: document.getElementById('username-input'),
    passwordInput: document.getElementById('password-input'),
    loginSubmit: document.getElementById('login-submit'),
    loginCancel: document.getElementById('login-cancel')
};

// Initialize
async function init() {
    await loadModels();
    setupEventListeners();
    checkAuthStatus();
    
    // Auto-resize textarea
    elements.messageInput.addEventListener('input', () => {
        elements.messageInput.style.height = 'auto';
        elements.messageInput.style.height = elements.messageInput.scrollHeight + 'px';
    });
}

// Load available Ollama models
async function loadModels() {
    try {
        const response = await fetch('/api/chat/models');
        const data = await response.json();
        availableModels = data.models || [];
        
        // Populate select
        elements.modelSelect.innerHTML = availableModels.map(m => 
            `<option value="${m.name}">${m.name}</option>`
        ).join('');
        
        // Select default - gpt-oss para Saulo
        const defaultModel = availableModels.find(m => 
            m.name.includes('gpt-oss')
        ) || availableModels[0];
        if (defaultModel) {
            elements.modelSelect.value = defaultModel.name;
        }
    } catch (err) {
        console.error('Failed to load models:', err);
        elements.modelSelect.innerHTML = '<option value="">Error cargando modelos</option>';
    }
}

// Setup event listeners
function setupEventListeners() {
    // Send message
    elements.sendBtn.addEventListener('click', sendMessage);
    elements.messageInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
    
    // Enable/disable send button
    elements.messageInput.addEventListener('input', () => {
        elements.sendBtn.disabled = !elements.messageInput.value.trim();
    });
    
    // New chat
    elements.newChatBtn.addEventListener('click', startNewChat);
    
    // Admin login
    elements.adminBtn.addEventListener('click', () => {
        if (authToken) {
            logout();
        } else {
            showLoginModal();
        }
    });
    
    elements.loginSubmit.addEventListener('click', doLogin);
    elements.loginCancel.addEventListener('click', hideLoginModal);
    elements.passwordInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') doLogin();
    });
    
    // Mobile menu - Fixed for mobile
    elements.menuToggle.addEventListener('click', () => {
        if (window.innerWidth <= 768) {
            elements.sidebar.classList.toggle('visible');
        }
    });
    
    // Close sidebar when clicking outside on mobile
    elements.chatContainer.addEventListener('click', (e) => {
        if (window.innerWidth <= 768 && elements.sidebar.classList.contains('visible')) {
            elements.sidebar.classList.remove('visible');
        }
    });
}

// Check auth status
function checkAuthStatus() {
    if (authToken) {
        elements.adminBtn.textContent = '👤 Salir';
        // Verify token is valid
        fetch('/api/auth/me', {
            headers: { 'Authorization': `Bearer ${authToken}` }
        }).catch(() => {
            logout();
        });
    } else {
        elements.adminBtn.textContent = '👤 Admin';
        elements.langostaBadge.classList.add('hidden');
    }
}

// Login
async function doLogin() {
    const username = elements.usernameInput.value;
    const password = elements.passwordInput.value;
    
    try {
        const response = await fetch('/api/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });
        
        if (response.ok) {
            const data = await response.json();
            authToken = data.access_token;
            localStorage.setItem('saulo_token', authToken);
            elements.adminBtn.textContent = '👤 Salir';
            hideLoginModal();
            showToast('✅ Admin mode activado');
        } else {
            showToast('❌ Credenciales incorrectas');
        }
    } catch (err) {
        showToast('❌ Error de conexión');
    }
}

// Logout
function logout() {
    authToken = null;
    localStorage.removeItem('saulo_token');
    elements.adminBtn.textContent = '👤 Admin';
    elements.langostaBadge.classList.add('hidden');
    isLangostaMode = false;
    showToast('👋 Sesión cerrada');
}

// Show/hide modal - Fixed to use CSS classes
function showLoginModal() {
    elements.loginModal.classList.remove('hidden');
    elements.loginModal.classList.add('visible');
    elements.passwordInput.focus();
}

function hideLoginModal() {
    elements.loginModal.classList.remove('visible');
    elements.loginModal.classList.add('hidden');
    elements.passwordInput.value = '';
}

// Start new chat
function startNewChat() {
    currentConversationId = null;
    elements.messagesContainer.innerHTML = `
        <div class="welcome-message">
            <h2>¡Hola! Soy Saulo</h2>
            <p>Puedo ayudarte con:</p>
            <ul>
                <li>🩺 <strong>Consultas médicas</strong> - Busco evidencia y te resumo estudios</li>
                <li>💻 <strong>Código</strong> - Uso modelos especializados para programación</li>
                <li>💬 <strong>Preguntas generales</strong> - Chats cotidianos y consultas varias</li>
            </ul>
            <p class="hint">Escribe tu mensaje abajo para comenzar.</p>
        </div>
    `;
    elements.messageInput.value = '';
    elements.sendBtn.disabled = true;
    
    // On mobile, hide sidebar
    if (window.innerWidth <= 768) {
        elements.sidebar.classList.add('hidden');
    }
}

// Send message
async function sendMessage() {
    const content = elements.messageInput.value.trim();
    if (!content) return;
    
    // Check for @langosta command
    if (content.toLowerCase().startsWith('@langosta')) {
        if (!authToken) {
            showToast('🔒 Necesitas iniciar sesión como admin para usar Langosta');
            showLoginModal();
            return;
        }
        isLangostaMode = true;
        elements.langostaBadge.classList.remove('hidden');
    }
    
    // Add user message to UI
    addMessage(content, 'user');
    
    // Clear input
    elements.messageInput.value = '';
    elements.messageInput.style.height = 'auto';
    elements.sendBtn.disabled = true;
    
    // Show loading
    const loadingId = showLoading();
    
    try {
        const response = await fetch('/api/chat/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                ...(authToken && { 'Authorization': `Bearer ${authToken}` })
            },
            body: JSON.stringify({
                content: content,
                model: elements.modelSelect.value,
                conversation_id: currentConversationId
            })
        });
        
        hideLoading(loadingId);
        
        if (response.ok) {
            const data = await response.json();
            currentConversationId = data.conversation_id;
            addMessage(data.text, 'assistant');
            updateConversationList();
        } else {
            addMessage('❌ Error al procesar tu mensaje. Intenta de nuevo.', 'assistant');
        }
    } catch (err) {
        hideLoading(loadingId);
        addMessage('❌ Error de conexión. Verifica que el servidor esté corriendo.', 'assistant');
    }
}

// Add message to UI
function addMessage(text, role) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;
    
    // Simple markdown-like formatting
    let formattedText = text
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>')
        .replace(/`([^`]+)`/g, '<code>$1</code>')
        .replace(/\n/g, '<br>');
    
    messageDiv.innerHTML = `<div class="message-content">${formattedText}</div>`;
    
    // Remove welcome message if present
    const welcome = elements.messagesContainer.querySelector('.welcome-message');
    if (welcome) welcome.remove();
    
    elements.messagesContainer.appendChild(messageDiv);
    scrollToBottom();
}

// Show loading indicator
function showLoading() {
    const id = 'loading-' + Date.now();
    const loadingDiv = document.createElement('div');
    loadingDiv.id = id;
    loadingDiv.className = 'message assistant';
    loadingDiv.innerHTML = `
        <div class="loading-indicator">
            <span></span><span></span><span></span>
        </div>
    `;
    elements.messagesContainer.appendChild(loadingDiv);
    scrollToBottom();
    return id;
}

// Hide loading
function hideLoading(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
}

// Scroll to bottom
function scrollToBottom() {
    elements.messagesContainer.scrollTop = elements.messagesContainer.scrollHeight;
}

// Update conversation list (simplified)
function updateConversationList() {
    // In a full implementation, this would fetch from the server
    // For now, we just show the current conversation
}

// Show toast notification
function showToast(message) {
    const toast = document.createElement('div');
    toast.style.cssText = `
        position: fixed;
        bottom: 80px;
        left: 50%;
        transform: translateX(-50%);
        background: var(--bg-secondary);
        color: var(--text-primary);
        padding: 12px 20px;
        border-radius: 8px;
        border: 1px solid var(--border);
        z-index: 1000;
        font-size: 14px;
    `;
    toast.textContent = message;
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.remove();
    }, 3000);
}

// Start
init();