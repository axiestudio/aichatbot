(function() {
  'use strict';
  
  // Prevent multiple initializations
  if (window.AxieChatWidget) {
    return;
  }
  
  // Configuration
  const config = window.AxieChatConfig || {};
  const API_URL = config.apiUrl || 'https://chat.axiestudio.se/api/v1';
  const TENANT_ID = config.tenantId;
  const CONFIG_ID = config.configId;
  
  if (!TENANT_ID || !CONFIG_ID) {
    console.error('Axie Chat Widget: Missing tenantId or configId');
    return;
  }
  
  // Widget state
  let isOpen = false;
  let isLoaded = false;
  let chatConfig = null;
  let messages = [];
  let sessionId = generateSessionId();
  
  // Create widget container
  function createWidget() {
    const container = document.createElement('div');
    container.id = 'axie-chat-widget';
    container.innerHTML = `
      <div id="axie-chat-button" class="axie-chat-button">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </div>
      <div id="axie-chat-window" class="axie-chat-window" style="display: none;">
        <div class="axie-chat-header">
          <div class="axie-chat-title">
            <div class="axie-chat-avatar">
              <img src="https://www.axiestudio.se/Axiestudiologo.jpg" alt="Axie Studio" />
            </div>
            <div class="axie-chat-info">
              <div class="axie-chat-name">AI Assistant</div>
              <div class="axie-chat-status">Online</div>
            </div>
          </div>
          <button id="axie-chat-close" class="axie-chat-close">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <line x1="18" y1="6" x2="6" y2="18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              <line x1="6" y1="6" x2="18" y2="18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            </svg>
          </button>
        </div>
        <div id="axie-chat-messages" class="axie-chat-messages"></div>
        <div class="axie-chat-input-container">
          <input 
            type="text" 
            id="axie-chat-input" 
            class="axie-chat-input" 
            placeholder="Type your message..."
          />
          <button id="axie-chat-send" class="axie-chat-send">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <line x1="22" y1="2" x2="11" y2="13" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
              <polygon points="22,2 15,22 11,13 2,9 22,2" fill="currentColor"/>
            </svg>
          </button>
        </div>
        <div class="axie-chat-footer">
          Powered by <a href="https://axiestudio.se" target="_blank">Axie Studio</a>
        </div>
      </div>
    `;
    
    document.body.appendChild(container);
    return container;
  }
  
  // Load CSS styles
  function loadStyles() {
    const styles = `
      #axie-chat-widget {
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 10000;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
      }
      
      .axie-chat-button {
        width: 60px;
        height: 60px;
        border-radius: 50%;
        background: #2563eb;
        color: white;
        border: none;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
        transition: all 0.3s ease;
      }
      
      .axie-chat-button:hover {
        transform: scale(1.05);
        box-shadow: 0 6px 16px rgba(37, 99, 235, 0.4);
      }
      
      .axie-chat-window {
        position: absolute;
        bottom: 80px;
        right: 0;
        width: 380px;
        height: 500px;
        background: white;
        border-radius: 12px;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
        display: flex;
        flex-direction: column;
        overflow: hidden;
        animation: slideUp 0.3s ease;
      }
      
      @keyframes slideUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
      }
      
      .axie-chat-header {
        background: #2563eb;
        color: white;
        padding: 16px;
        display: flex;
        align-items: center;
        justify-content: space-between;
      }
      
      .axie-chat-title {
        display: flex;
        align-items: center;
        gap: 12px;
      }
      
      .axie-chat-avatar img {
        width: 32px;
        height: 32px;
        border-radius: 50%;
        object-fit: cover;
      }
      
      .axie-chat-name {
        font-weight: 600;
        font-size: 14px;
      }
      
      .axie-chat-status {
        font-size: 12px;
        opacity: 0.8;
      }
      
      .axie-chat-close {
        background: none;
        border: none;
        color: white;
        cursor: pointer;
        padding: 4px;
        border-radius: 4px;
        opacity: 0.8;
        transition: opacity 0.2s;
      }
      
      .axie-chat-close:hover {
        opacity: 1;
      }
      
      .axie-chat-messages {
        flex: 1;
        padding: 16px;
        overflow-y: auto;
        display: flex;
        flex-direction: column;
        gap: 12px;
      }
      
      .axie-message {
        max-width: 80%;
        padding: 8px 12px;
        border-radius: 12px;
        font-size: 14px;
        line-height: 1.4;
      }
      
      .axie-message.assistant {
        background: #f3f4f6;
        color: #374151;
        align-self: flex-start;
      }
      
      .axie-message.user {
        background: #2563eb;
        color: white;
        align-self: flex-end;
      }
      
      .axie-chat-input-container {
        padding: 16px;
        border-top: 1px solid #e5e7eb;
        display: flex;
        gap: 8px;
      }
      
      .axie-chat-input {
        flex: 1;
        padding: 8px 12px;
        border: 1px solid #d1d5db;
        border-radius: 20px;
        outline: none;
        font-size: 14px;
      }
      
      .axie-chat-input:focus {
        border-color: #2563eb;
      }
      
      .axie-chat-send {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        background: #2563eb;
        color: white;
        border: none;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: background 0.2s;
      }
      
      .axie-chat-send:hover {
        background: #1d4ed8;
      }
      
      .axie-chat-footer {
        padding: 8px 16px;
        text-align: center;
        font-size: 11px;
        color: #6b7280;
        border-top: 1px solid #f3f4f6;
      }
      
      .axie-chat-footer a {
        color: #2563eb;
        text-decoration: none;
      }
      
      @media (max-width: 480px) {
        .axie-chat-window {
          width: calc(100vw - 40px);
          height: calc(100vh - 120px);
          bottom: 80px;
          right: 20px;
        }
      }
    `;
    
    const styleSheet = document.createElement('style');
    styleSheet.textContent = styles;
    document.head.appendChild(styleSheet);
  }
  
  // Generate session ID
  function generateSessionId() {
    return 'session_' + Math.random().toString(36).substr(2, 9) + '_' + Date.now();
  }
  
  // Load chat configuration
  async function loadConfig() {
    try {
      const response = await fetch(`${API_URL}/embed/config/${TENANT_ID}/${CONFIG_ID}`);
      if (response.ok) {
        chatConfig = await response.json();
        applyConfig();
      }
    } catch (error) {
      console.error('Failed to load chat config:', error);
    }
  }
  
  // Apply configuration to widget
  function applyConfig() {
    if (!chatConfig) return;
    
    const button = document.getElementById('axie-chat-button');
    const window = document.getElementById('axie-chat-window');
    const input = document.getElementById('axie-chat-input');
    
    if (button) {
      button.style.background = chatConfig.primaryColor || '#2563eb';
    }
    
    if (input) {
      input.placeholder = chatConfig.placeholder || 'Type your message...';
    }
    
    // Add welcome message
    if (chatConfig.welcomeMessage && messages.length === 0) {
      addMessage('assistant', chatConfig.welcomeMessage);
    }
  }
  
  // Add message to chat
  function addMessage(role, content) {
    const messagesContainer = document.getElementById('axie-chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `axie-message ${role}`;
    messageDiv.textContent = content;
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    
    messages.push({ role, content, timestamp: new Date() });
  }
  
  // Send message
  async function sendMessage(content) {
    addMessage('user', content);
    
    try {
      const response = await fetch(`${API_URL}/embed/chat/${TENANT_ID}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          sessionId,
          message: content,
          configId: CONFIG_ID
        })
      });
      
      if (response.ok) {
        const data = await response.json();
        addMessage('assistant', data.response);
      } else {
        addMessage('assistant', 'Sorry, I encountered an error. Please try again.');
      }
    } catch (error) {
      addMessage('assistant', 'Sorry, I encountered an error. Please try again.');
    }
  }
  
  // Initialize widget
  function init() {
    if (isLoaded) return;
    
    loadStyles();
    const widget = createWidget();
    
    // Event listeners
    const button = document.getElementById('axie-chat-button');
    const closeBtn = document.getElementById('axie-chat-close');
    const input = document.getElementById('axie-chat-input');
    const sendBtn = document.getElementById('axie-chat-send');
    const chatWindow = document.getElementById('axie-chat-window');
    
    button.addEventListener('click', () => {
      isOpen = !isOpen;
      chatWindow.style.display = isOpen ? 'flex' : 'none';
    });
    
    closeBtn.addEventListener('click', () => {
      isOpen = false;
      chatWindow.style.display = 'none';
    });
    
    input.addEventListener('keypress', (e) => {
      if (e.key === 'Enter' && input.value.trim()) {
        sendMessage(input.value.trim());
        input.value = '';
      }
    });
    
    sendBtn.addEventListener('click', () => {
      if (input.value.trim()) {
        sendMessage(input.value.trim());
        input.value = '';
      }
    });
    
    // Load configuration
    loadConfig();
    
    isLoaded = true;
  }
  
  // Auto-initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
  
  // Expose widget API
  window.AxieChatWidget = {
    open: () => {
      isOpen = true;
      document.getElementById('axie-chat-window').style.display = 'flex';
    },
    close: () => {
      isOpen = false;
      document.getElementById('axie-chat-window').style.display = 'none';
    },
    sendMessage: (message) => {
      if (typeof message === 'string' && message.trim()) {
        sendMessage(message.trim());
      }
    }
  };
  
})();
