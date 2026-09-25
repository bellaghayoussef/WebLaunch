/**
 * AgentX Client Application
 * Handles SSE Streaming, ReAct Visualizer, Markdown Rendering, and Settings
 */

document.addEventListener('DOMContentLoaded', () => {
  // DOM Elements
  const chatContainer = document.getElementById('chat-container');
  const messagesList = document.getElementById('messages-list');
  const welcomeHero = document.getElementById('welcome-hero');
  const chatForm = document.getElementById('chat-form');
  const promptInput = document.getElementById('prompt-input');
  const sendBtn = document.getElementById('send-btn');
  const newChatBtn = document.getElementById('new-chat-btn');
  const clearChatBtn = document.getElementById('clear-chat-btn');
  const activityBanner = document.getElementById('agent-activity-banner');
  const activityText = document.getElementById('activity-text');
  const activeModelName = document.getElementById('active-model-name');
  const currentModelTag = document.getElementById('current-model-tag');
  const currentEndpointTag = document.getElementById('current-endpoint-tag');
  const fileTreeContainer = document.getElementById('file-tree-container');
  const refreshFilesBtn = document.getElementById('refresh-files-btn');
  const themeToggleBtn = document.getElementById('theme-toggle-btn');
  const shortcutSearch = document.getElementById('shortcut-search');
  
  // Settings modal elements
  const openSettingsBtn = document.getElementById('open-settings-btn');
  const closeSettingsBtn = document.getElementById('close-settings-btn');
  const cancelSettingsBtn = document.getElementById('cancel-settings-btn');
  const settingsModal = document.getElementById('settings-modal');
  const settingsForm = document.getElementById('settings-form');
  const cfgBaseurl = document.getElementById('cfg-baseurl');
  const cfgToken = document.getElementById('cfg-token');
  const cfgModel = document.getElementById('cfg-model');
  const cfgTheme = document.getElementById('cfg-theme');
  const toggleTokenVis = document.getElementById('toggle-token-vis');

  // Mobile menu
  const mobileMenuBtn = document.getElementById('mobile-menu-btn');
  const sidebar = document.getElementById('sidebar');

  let isGenerating = false;
  let conversationHistory = [];

  // Configure Marked options
  if (window.marked) {
    marked.setOptions({
      breaks: true,
      gfm: true
    });
  }

  // Load Initial Configuration
  async function loadConfig() {
    try {
      const res = await fetch('/api/config');
      const data = await res.json();
      activeModelName.textContent = data.model;
      currentModelTag.textContent = data.model;
      
      const cleanUrl = data.baseURL.replace(/^https?:\/\//, '');
      currentEndpointTag.textContent = cleanUrl;
      
      cfgBaseurl.value = data.baseURL || '';
      cfgModel.value = data.model || 'claude-opus-4-8';
      cfgTheme.value = data.theme || 'dark';

      // Set document theme
      document.documentElement.setAttribute('data-theme', data.theme || 'dark');
      updateThemeIcon(data.theme || 'dark');
    } catch (err) {
      console.warn('Could not load config:', err);
    }
  }

  // Load Workspace Files
  async function loadWorkspaceFiles() {
    try {
      const res = await fetch('/api/workspace');
      const data = await res.json();
      if (data.files && Array.isArray(data.files)) {
        fileTreeContainer.innerHTML = '';
        data.files.forEach(f => {
          const item = document.createElement('div');
          item.className = `file-entry ${f.type === 'directory' ? 'dir' : 'file'}`;
          item.innerHTML = `
            <i class="fa-solid ${f.type === 'directory' ? 'fa-folder' : 'fa-file-lines'}"></i>
            <span>${escapeHtml(f.name)}</span>
          `;
          fileTreeContainer.appendChild(item);
        });
      }
    } catch (e) {
      fileTreeContainer.innerHTML = '<div class="file-item-loading">Files unavailable</div>';
    }
  }

  // Quick Prompt cards
  document.querySelectorAll('.quick-prompt-card').forEach(card => {
    card.addEventListener('click', () => {
      const prompt = card.getAttribute('data-prompt');
      if (prompt) {
        promptInput.value = prompt;
        autoResizeTextarea();
        submitPrompt(prompt);
      }
    });
  });

  // Auto-resize textarea
  promptInput.addEventListener('input', autoResizeTextarea);
  function autoResizeTextarea() {
    promptInput.style.height = 'auto';
    promptInput.style.height = Math.min(promptInput.scrollHeight, 180) + 'px';
  }

  // Textarea key listener (Enter to send, Shift+Enter for newline)
  promptInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      const val = promptInput.value.trim();
      if (val && !isGenerating) {
        submitPrompt(val);
      }
    }
  });

  // Form submit
  chatForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const val = promptInput.value.trim();
    if (val && !isGenerating) {
      submitPrompt(val);
    }
  });

  // Shortcut for search
  if (shortcutSearch) {
    shortcutSearch.addEventListener('click', () => {
      if (!promptInput.value.startsWith('Cherche sur le web : ')) {
        promptInput.value = 'Cherche sur le web : ' + promptInput.value;
      }
      promptInput.focus();
      autoResizeTextarea();
    });
  }

  // Submit Prompt to Agent via SSE Stream
  async function submitPrompt(promptText) {
    if (isGenerating) return;
    isGenerating = true;
    sendBtn.disabled = true;

    // Hide welcome hero if first message
    if (welcomeHero) {
      welcomeHero.style.display = 'none';
    }

    // Append User Message
    appendUserMessage(promptText);
    promptInput.value = '';
    promptInput.style.height = 'auto';

    // Show Agent Activity Banner
    setActivity('AgentX démarre la réflexion...', true);

    // Create Agent Message Block
    const agentMsgElements = createAgentMessageBlock();
    scrollToBottom();

    // Prepare payload
    conversationHistory.push({ role: 'user', content: promptText });

    try {
      const response = await fetch('/api/agent/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          prompt: promptText,
          messages: conversationHistory,
          model: activeModelName.textContent
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder('utf-8');
      let buffer = '';
      let accumulatedText = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          const trimmed = line.trim();
          if (!trimmed.startsWith('data: ')) continue;
          const jsonStr = trimmed.slice(6);
          if (jsonStr === '[DONE]') continue;

          try {
            const event = JSON.parse(jsonStr);
            handleAgentEvent(event, agentMsgElements, (text) => {
              accumulatedText = text;
            });
          } catch (err) {
            console.error('Error parsing SSE event:', err);
          }
        }
      }

      // Finish conversation turn
      if (accumulatedText) {
        conversationHistory.push({ role: 'assistant', content: accumulatedText });
      }

    } catch (err) {
      console.error('Execution error:', err);
      agentMsgElements.markdownContainer.innerHTML += `
        <div style="color: var(--accent-rose); background: rgba(244, 63, 94, 0.1); padding: 0.8rem; border-radius: 8px; border: 1px solid var(--accent-rose); margin-top: 0.5rem;">
          <i class="fa-solid fa-triangle-exclamation"></i> <strong>Erreur:</strong> ${escapeHtml(err.message)}
        </div>
      `;
    } finally {
      isGenerating = false;
      sendBtn.disabled = false;
      setActivity('', false);
      scrollToBottom();
      // Re-highlight any newly rendered code blocks
      if (window.Prism) {
        Prism.highlightAllUnder(agentMsgElements.markdownContainer);
      }
      attachCopyButtons(agentMsgElements.markdownContainer);
    }
  }

  // Handle individual ReAct agent events
  function handleAgentEvent(event, elements, updateAccumulated) {
    const { body, stepBadge, thinkingBox, thinkingContent, toolsContainer, markdownContainer } = elements;

    switch (event.type) {
      case 'agent:start':
        setActivity(`AgentX connecté (${event.model})`, true);
        break;

      case 'agent:step_start':
        stepBadge.style.display = 'inline-flex';
        stepBadge.innerHTML = `<i class="fa-solid fa-arrows-spin fa-spin"></i> Étape ${event.step}`;
        setActivity(`Étape ${event.step}: Raisonnement en cours...`, true);
        break;

      case 'agent:thought':
        thinkingBox.style.display = 'block';
        thinkingContent.textContent += (thinkingContent.textContent ? '\n' : '') + event.thought;
        setActivity(`AgentX réfléchit...`, true);
        scrollToBottom();
        break;

      case 'agent:tool_call': {
        setActivity(`Exécution de l'outil "${event.name}"...`, true);
        const card = document.createElement('div');
        card.className = 'tool-call-card';
        card.id = `tool-${event.id}`;
        
        let icon = 'fa-bolt';
        if (event.name === 'web_search') icon = 'fa-globe';
        else if (event.name === 'fetch_url') icon = 'fa-link';
        else if (event.name === 'run_javascript') icon = 'fa-code';
        else if (event.name.includes('file')) icon = 'fa-folder';
        else if (event.name.includes('time')) icon = 'fa-clock';

        card.innerHTML = `
          <div class="tool-call-header">
            <span class="tool-call-title">
              <i class="fa-solid ${icon}"></i> Outil : <span class="tool-badge-name">${escapeHtml(event.name)}</span>
            </span>
            <span class="tool-status-pill"><i class="fa-solid fa-circle-notch fa-spin"></i> En cours</span>
          </div>
          <div class="tool-details">
            <div class="tool-io-block">
              <strong>Paramètres:</strong>
              <div class="tool-io-content">${escapeHtml(JSON.stringify(event.input, null, 2))}</div>
            </div>
          </div>
        `;
        toolsContainer.appendChild(card);
        scrollToBottom();
        break;
      }

      case 'agent:tool_result': {
        const card = document.getElementById(`tool-${event.id}`);
        if (card) {
          const statusPill = card.querySelector('.tool-status-pill');
          if (statusPill) {
            statusPill.innerHTML = `<i class="fa-solid fa-check"></i> Terminé`;
            statusPill.style.color = 'var(--accent-emerald)';
          }
          const details = card.querySelector('.tool-details');
          if (details) {
            const resBlock = document.createElement('div');
            resBlock.className = 'tool-io-block';
            resBlock.innerHTML = `
              <strong>Résultat:</strong>
              <div class="tool-io-content">${escapeHtml(JSON.stringify(event.result, null, 2))}</div>
            `;
            details.appendChild(resBlock);
          }
        }
        setActivity(`Résultats de l'outil reçus. Synthèse en cours...`, true);
        scrollToBottom();
        break;
      }

      case 'agent:message_chunk': {
        updateAccumulated(event.text);
        if (window.marked) {
          markdownContainer.innerHTML = marked.parse(event.text);
        } else {
          markdownContainer.textContent = event.text;
        }
        scrollToBottom();
        break;
      }

      case 'agent:finish': {
        stepBadge.innerHTML = `<i class="fa-solid fa-check-double"></i> Terminé (${event.stepsCount} étape${event.stepsCount > 1 ? 's' : ''})`;
        stepBadge.style.color = 'var(--accent-emerald)';
        stepBadge.style.borderColor = 'rgba(16, 185, 129, 0.3)';
        stepBadge.style.background = 'rgba(16, 185, 129, 0.1)';
        
        if (event.answer) {
          updateAccumulated(event.answer);
          if (window.marked) {
            markdownContainer.innerHTML = marked.parse(event.answer);
          } else {
            markdownContainer.textContent = event.answer;
          }
        }
        setActivity('', false);
        break;
      }
    }
  }

  // Create UI representation for user message
  function appendUserMessage(text) {
    const row = document.createElement('div');
    row.className = 'message-row user';
    row.innerHTML = `<div class="message-bubble user">${escapeHtml(text)}</div>`;
    messagesList.appendChild(row);
  }

  // Create UI template for assistant message with ReAct components
  function createAgentMessageBlock() {
    const row = document.createElement('div');
    row.className = 'message-row assistant';

    const avatar = document.createElement('div');
    avatar.className = 'assistant-avatar';
    avatar.innerHTML = `<i class="fa-solid fa-robot"></i>`;

    const body = document.createElement('div');
    body.className = 'assistant-body';

    // Step tracker badge
    const stepBadge = document.createElement('div');
    stepBadge.className = 'step-badge';
    stepBadge.style.display = 'none';

    // Thinking collapsible box
    const thinkingBox = document.createElement('div');
    thinkingBox.className = 'thinking-box';
    thinkingBox.style.display = 'none';
    thinkingBox.innerHTML = `
      <div class="thinking-header">
        <span class="thinking-title"><i class="fa-solid fa-brain"></i> Raisonnement interne (Thinking)</span>
        <i class="fa-solid fa-chevron-down thinking-toggle-icon"></i>
      </div>
      <div class="thinking-content"></div>
    `;

    // Collapsible toggle handler
    const thinkingHeader = thinkingBox.querySelector('.thinking-header');
    thinkingHeader.addEventListener('click', () => {
      thinkingBox.classList.toggle('collapsed');
    });

    // Tools container
    const toolsContainer = document.createElement('div');
    toolsContainer.className = 'tools-container';
    toolsContainer.style.display = 'flex';
    toolsContainer.style.flexDirection = 'column';
    toolsContainer.style.gap = '0.5rem';

    // Markdown text container
    const markdownContainer = document.createElement('div');
    markdownContainer.className = 'markdown-body';

    body.appendChild(stepBadge);
    body.appendChild(thinkingBox);
    body.appendChild(toolsContainer);
    body.appendChild(markdownContainer);

    row.appendChild(avatar);
    row.appendChild(body);
    messagesList.appendChild(row);

    return {
      row,
      body,
      stepBadge,
      thinkingBox,
      thinkingContent: thinkingBox.querySelector('.thinking-content'),
      toolsContainer,
      markdownContainer
    };
  }

  function setActivity(text, show) {
    if (show) {
      activityText.textContent = text;
      activityBanner.style.display = 'flex';
    } else {
      activityBanner.style.display = 'none';
    }
  }

  function scrollToBottom() {
    chatContainer.scrollTop = chatContainer.scrollHeight;
  }

  function escapeHtml(str) {
    if (typeof str !== 'string') return String(str);
    return str
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  // Code Copy Buttons
  function attachCopyButtons(container) {
    container.querySelectorAll('pre').forEach(pre => {
      if (pre.querySelector('.copy-code-btn')) return;
      
      const wrapper = document.createElement('div');
      wrapper.className = 'code-block-wrapper';
      pre.parentNode.insertBefore(wrapper, pre);
      wrapper.appendChild(pre);

      const btn = document.createElement('button');
      btn.className = 'copy-code-btn';
      btn.innerHTML = '<i class="fa-solid fa-copy"></i> Copier';
      btn.addEventListener('click', () => {
        const code = pre.querySelector('code')?.innerText || pre.innerText;
        navigator.clipboard.writeText(code).then(() => {
          btn.innerHTML = '<i class="fa-solid fa-check"></i> Copié!';
          setTimeout(() => {
            btn.innerHTML = '<i class="fa-solid fa-copy"></i> Copier';
          }, 2000);
        });
      });
      wrapper.appendChild(btn);
    });
  }

  // Clear chat
  clearChatBtn.addEventListener('click', () => {
    if (confirm('Effacer la conversation en cours ?')) {
      messagesList.innerHTML = '';
      conversationHistory = [];
      welcomeHero.style.display = 'block';
    }
  });

  // New Chat
  newChatBtn.addEventListener('click', () => {
    messagesList.innerHTML = '';
    conversationHistory = [];
    welcomeHero.style.display = 'block';
    promptInput.value = '';
    promptInput.focus();
  });

  // Refresh files
  refreshFilesBtn.addEventListener('click', loadWorkspaceFiles);

  // Theme toggle
  themeToggleBtn.addEventListener('click', () => {
    const currentTheme = document.documentElement.getAttribute('data-theme') || 'dark';
    const nextTheme = currentTheme === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', nextTheme);
    updateThemeIcon(nextTheme);

    // Save to server
    fetch('/api/config', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ theme: nextTheme })
    }).catch(() => {});
  });

  function updateThemeIcon(theme) {
    const icon = themeToggleBtn.querySelector('i');
    if (theme === 'dark') {
      icon.className = 'fa-solid fa-moon';
    } else {
      icon.className = 'fa-solid fa-sun';
    }
  }

  // Settings Modal Handlers
  openSettingsBtn.addEventListener('click', () => {
    settingsModal.style.display = 'flex';
  });

  closeSettingsBtn.addEventListener('click', () => {
    settingsModal.style.display = 'none';
  });

  cancelSettingsBtn.addEventListener('click', () => {
    settingsModal.style.display = 'none';
  });

  settingsModal.addEventListener('click', (e) => {
    if (e.target === settingsModal) {
      settingsModal.style.display = 'none';
    }
  });

  toggleTokenVis.addEventListener('click', () => {
    const type = cfgToken.getAttribute('type') === 'password' ? 'text' : 'password';
    cfgToken.setAttribute('type', type);
    toggleTokenVis.innerHTML = `<i class="fa-solid fa-eye${type === 'password' ? '' : '-slash'}"></i>`;
  });

  settingsForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const saveBtn = document.getElementById('save-settings-btn');
    saveBtn.disabled = true;
    saveBtn.textContent = 'Enregistrement...';

    try {
      const payload = {
        baseURL: cfgBaseurl.value.trim(),
        apiKey: cfgToken.value.trim(),
        model: cfgModel.value,
        theme: cfgTheme.value
      };

      const res = await fetch('/api/config', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (!res.ok) throw new Error('Erreur lors de la sauvegarde');

      settingsModal.style.display = 'none';
      await loadConfig();
    } catch (err) {
      alert('Erreur: ' + err.message);
    } finally {
      saveBtn.disabled = false;
      saveBtn.textContent = 'Enregistrer les paramètres';
    }
  });

  // Mobile menu toggle
  if (mobileMenuBtn) {
    mobileMenuBtn.addEventListener('click', () => {
      sidebar.classList.toggle('open');
    });
  }

  // Init
  loadConfig();
  loadWorkspaceFiles();
});
