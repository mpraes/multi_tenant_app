class MultiTenantChatUI {
	constructor() {
		this.storageKey = 'multi-tenant-chat-ui-settings';
		this.historyKey = 'multi-tenant-chat-ui-history';
		this.sessionId = '';

		this.cacheElements();
		this.loadSettings();
		this.loadHistory();
		this.bindEvents();
		this.renderSession();
		this.handleInput();
		this.checkHealth();
		this.loadBotConfig();
	}

	cacheElements() {
		this.apiUrlInput = document.getElementById('apiUrl');
		this.userIdInput = document.getElementById('userId');
		this.saveSettingsButton = document.getElementById('saveSettings');
		this.checkHealthButton = document.getElementById('checkHealth');
		this.healthBadge = document.getElementById('healthBadge');
		this.sessionValue = document.getElementById('sessionValue');
		this.chatMessages = document.getElementById('chatMessages');
		this.typingIndicator = document.getElementById('typingIndicator');
		this.chatForm = document.getElementById('chatForm');
		this.messageInput = document.getElementById('messageInput');
		this.sendButton = document.getElementById('sendButton');
		this.charCount = document.getElementById('charCount');
		this.clearChatButton = document.getElementById('clearChat');
		this.quickActionButtons = document.querySelectorAll('.quick-action');

		// Config panel / Painel de configuracao
		this.toggleConfigButton = document.getElementById('toggleConfig');
		this.configForm = document.getElementById('configForm');
		this.configSummary = document.getElementById('configSummary');
		this.cfgName = document.getElementById('cfgName');
		this.cfgSystemPrompt = document.getElementById('cfgSystemPrompt');
		this.cfgLlmProvider = document.getElementById('cfgLlmProvider');
		this.cfgLlmModel = document.getElementById('cfgLlmModel');
		this.cfgTemperature = document.getElementById('cfgTemperature');
		this.cfgMaxTokens = document.getElementById('cfgMaxTokens');
		this.cfgRagEnabled = document.getElementById('cfgRagEnabled');
		this.cfgHistoryWindow = document.getElementById('cfgHistoryWindow');
		this.saveConfigButton = document.getElementById('saveConfig');
		this.resetConfigButton = document.getElementById('resetConfig');
		this.cfgSumName = document.getElementById('cfgSumName');
		this.cfgSumProvider = document.getElementById('cfgSumProvider');
		this.cfgSumModel = document.getElementById('cfgSumModel');
	}

	bindEvents() {
		this.chatForm.addEventListener('submit', (event) => {
			event.preventDefault();
			this.sendMessage();
		});

		this.messageInput.addEventListener('input', () => this.handleInput());
		this.messageInput.addEventListener('keydown', (event) => {
			if (event.key === 'Enter' && !event.shiftKey) {
				event.preventDefault();
				this.sendMessage();
			}
		});

		this.saveSettingsButton.addEventListener('click', () => this.saveSettings());
		this.checkHealthButton.addEventListener('click', () => this.checkHealth());
		this.clearChatButton.addEventListener('click', () => this.clearChat());

		this.quickActionButtons.forEach((button) => {
			button.addEventListener('click', () => {
				this.messageInput.value = button.dataset.message || '';
				this.handleInput();
				this.messageInput.focus();
			});
		});

		// Botoes das ferramentas de API / API tool buttons
		document.getElementById('btnHistory').addEventListener('click', () => this.fetchHistory());
		document.getElementById('btnSessions').addEventListener('click', () => this.fetchSessions());
		document.getElementById('btnStats').addEventListener('click', () => this.fetchStats());

		// Config panel toggle / Alternancia do painel de configuracao
		this.toggleConfigButton.addEventListener('click', () => this.toggleConfigPanel());
		this.saveConfigButton.addEventListener('click', () => this.saveBotConfig());
		this.resetConfigButton.addEventListener('click', () => this.resetBotConfig());
	}

	// Retorna as configuracoes atuais dos campos / Returns current field settings
	currentSettings() {
		return {
			apiUrl: this.apiUrlInput.value.trim().replace(/\/$/, ''),
			userId: this.userIdInput.value.trim() || 'web-user',
		};
	}

	// Exibe o historico da sessao atual / Shows history for the current session
	async fetchHistory() {
		if (!this.sessionId) {
			this.appendMessage('Sem sessao ativa. Envie uma mensagem primeiro.', 'assistant', 'api tools');
			return;
		}

		const { apiUrl } = this.currentSettings();

		try {
			const res = await fetch(`${apiUrl}/api/history/${this.sessionId}`);
			const data = await res.json();

			if (!res.ok) throw new Error(data.detail || `HTTP ${res.status}`);

			const lines = data.map((m) => `[${m.role}] ${m.content}`).join('\n');
			this.appendMessage(
				`Historico da sessao (${data.length} msgs):\n\n${lines}`,
				'assistant',
				'GET /api/history'
			);
		} catch (error) {
			this.appendMessage(`Erro: ${error.message}`, 'assistant', 'api tools');
		}
	}

	// Lista as sessoes do usuario atual / Lists sessions for the current user
	async fetchSessions() {
		const { apiUrl, userId } = this.currentSettings();

		try {
			const res = await fetch(`${apiUrl}/api/sessions/${userId}`);
			const data = await res.json();

			if (!res.ok) throw new Error(data.detail || `HTTP ${res.status}`);

			const lines = data.map((s) => `• ${s.session_id}  (${s.message_count} msgs)`).join('\n');
			this.appendMessage(
				`Sessoes do usuario "${userId}" (${data.length}):\n\n${lines || '(nenhuma)'}`,
				'assistant',
				'GET /api/sessions'
			);
		} catch (error) {
			this.appendMessage(`Erro: ${error.message}`, 'assistant', 'api tools');
		}
	}

	// Exibe estatisticas de uso / Shows usage stats
	async fetchStats() {
		const { apiUrl } = this.currentSettings();

		try {
			const res = await fetch(`${apiUrl}/api/stats`);
			const data = await res.json();

			if (!res.ok) throw new Error(data.detail || `HTTP ${res.status}`);

			const text = [
				`Mensagens: ${data.total_messages}`,
				`Tokens entrada: ${data.total_input_tokens}`,
				`Tokens saida: ${data.total_output_tokens}`,
				`Sessoes unicas: ${data.unique_sessions}`,
				`Usuarios unicos: ${data.unique_users}`,
			].join('\n');

			this.appendMessage(text, 'assistant', 'GET /api/stats');
		} catch (error) {
			this.appendMessage(`Erro: ${error.message}`, 'assistant', 'api tools');
		}
	}

	// ── Config panel / Painel de configuracao ────────────────────────────────

	// Alterna entre resumo e formulario / Toggles between summary and form
	toggleConfigPanel() {
		const isEditing = !this.configForm.classList.contains('hidden');
		this.configForm.classList.toggle('hidden', isEditing);
		this.configSummary.classList.toggle('hidden', !isEditing);
		this.toggleConfigButton.textContent = isEditing ? 'editar' : 'fechar';
	}

	// Preenche o formulario com os dados da API / Populates the form with API data
	_populateConfigForm(data) {
		this.cfgName.value = data.name || '';
		this.cfgSystemPrompt.value = data.system_prompt || '';
		this.cfgLlmProvider.value = data.llm_provider || '';
		this.cfgLlmModel.value = data.llm_model || '';
		this.cfgTemperature.value = data.llm_temperature ?? 0.7;
		this.cfgMaxTokens.value = data.llm_max_tokens ?? 1024;
		this.cfgRagEnabled.checked = !!data.rag_enabled;
		this.cfgHistoryWindow.value = data.history_window ?? 10;

		this.cfgSumName.textContent = data.name || '-';
		this.cfgSumProvider.textContent = data.llm_provider || 'padrao';
		this.cfgSumModel.textContent = data.llm_model || 'padrao';
	}

	// Busca e exibe a configuracao atual / Fetches and displays the current config
	async loadBotConfig() {
		const { apiUrl } = this.currentSettings();
		try {
			const res = await fetch(`${apiUrl}/api/config`);
			if (!res.ok) return;
			const data = await res.json();
			this._populateConfigForm(data);
		} catch (_) {
			// silencioso na carga inicial / silent on initial load
		}
	}

	// Envia as alteracoes para a API / Sends changes to the API
	async saveBotConfig() {
		const { apiUrl } = this.currentSettings();

		const body = {
			name: this.cfgName.value.trim() || null,
			system_prompt: this.cfgSystemPrompt.value.trim() || null,
			llm_provider: this.cfgLlmProvider.value || null,
			llm_model: this.cfgLlmModel.value.trim() || null,
			llm_temperature: parseFloat(this.cfgTemperature.value),
			llm_max_tokens: parseInt(this.cfgMaxTokens.value, 10),
			rag_enabled: this.cfgRagEnabled.checked,
			history_window: parseInt(this.cfgHistoryWindow.value, 10),
		};

		// Remove nulos para nao sobrescrever campos nao editados
		// Remove nulls to avoid overwriting untouched fields
		Object.keys(body).forEach((k) => body[k] === null && delete body[k]);

		try {
			const res = await fetch(`${apiUrl}/api/config`, {
				method: 'PUT',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify(body),
			});
			const data = await res.json();
			if (!res.ok) throw new Error(data.detail || `HTTP ${res.status}`);

			this._populateConfigForm(data);
			this.toggleConfigPanel();
			this.appendMessage('Configuracao salva. Reinicie o servidor para aplicar alteracoes de modelo/provider.', 'assistant', 'PUT /api/config');
		} catch (error) {
			this.appendMessage(`Erro ao salvar config: ${error.message}`, 'assistant', 'api config');
		}
	}

	// Reseta a configuracao para os defaults / Resets config to defaults
	async resetBotConfig() {
		const { apiUrl } = this.currentSettings();
		try {
			const res = await fetch(`${apiUrl}/api/config`, { method: 'DELETE' });
			if (!res.ok) {
				const data = await res.json().catch(() => ({}));
				throw new Error(data.detail || `HTTP ${res.status}`);
			}
			await this.loadBotConfig();
			this.toggleConfigPanel();
			this.appendMessage('Configuracao resetada para os defaults.', 'assistant', 'DELETE /api/config');
		} catch (error) {
			this.appendMessage(`Erro ao resetar config: ${error.message}`, 'assistant', 'api config');
		}
	}

	handleInput() {
		const messageLength = this.messageInput.value.trim().length;
		this.charCount.textContent = `${this.messageInput.value.length} / 2000`;
		this.sendButton.disabled = messageLength === 0;

		this.messageInput.style.height = 'auto';
		this.messageInput.style.height = `${Math.min(this.messageInput.scrollHeight, 180)}px`;
	}

	loadSettings() {
		try {
			const rawSettings = localStorage.getItem(this.storageKey);
			if (!rawSettings) {
				return;
			}

			const settings = JSON.parse(rawSettings);
			this.apiUrlInput.value = settings.apiUrl || this.apiUrlInput.value;
			this.userIdInput.value = settings.userId || this.userIdInput.value;
			this.sessionId = settings.sessionId || '';
		} catch (error) {
			console.warn('Falha ao carregar configuracoes:', error);
		}
	}

	saveSettings() {
		const settings = {
			apiUrl: this.apiUrlInput.value.trim() || 'http://localhost:8000',
			userId: this.userIdInput.value.trim() || 'web-user',
			sessionId: this.sessionId,
		};

		localStorage.setItem(this.storageKey, JSON.stringify(settings));
		this.renderSession();
		this.flashHealth('saved', 'configurado');
	}

	loadHistory() {
		try {
			const rawHistory = localStorage.getItem(this.historyKey);
			if (!rawHistory) {
				return;
			}

			const items = JSON.parse(rawHistory);
			if (!Array.isArray(items) || items.length === 0) {
				return;
			}

			this.chatMessages.innerHTML = '';
			items.forEach((item) => this.appendMessage(item.text, item.role, item.meta));
		} catch (error) {
			console.warn('Falha ao carregar historico:', error);
		}
	}

	persistHistory() {
		const items = Array.from(this.chatMessages.querySelectorAll('.message')).map((message) => {
			const role = message.classList.contains('user-message') ? 'user' : 'assistant';
			const text = message.querySelector('.bubble')?.textContent || '';
			const meta = message.querySelector('.message-meta')?.textContent || '';
			return { role, text, meta };
		});

		localStorage.setItem(this.historyKey, JSON.stringify(items));
	}

	renderSession() {
		this.sessionValue.textContent = this.sessionId || 'nova sessao';
	}

	buildEndpoint() {
		const apiUrl = this.apiUrlInput.value.trim().replace(/\/$/, '');

		if (!apiUrl) {
			throw new Error('Informe a API base URL.');
		}

		return `${apiUrl}/chat`;
	}

	async sendMessage() {
		const text = this.messageInput.value.trim();
		if (!text) {
			return;
		}

		let endpoint;
		try {
			endpoint = this.buildEndpoint();
		} catch (error) {
			this.appendMessage(error.message, 'assistant', 'erro de configuracao');
			return;
		}

		const payload = {
			user_id: this.userIdInput.value.trim() || 'web-user',
			text,
			session_id: this.sessionId,
		};

		this.appendMessage(text, 'user', this.formatNow());
		this.messageInput.value = '';
		this.handleInput();
		this.toggleTyping(true);

		try {
			const response = await fetch(endpoint, {
				method: 'POST',
				headers: {
					'Content-Type': 'application/json',
				},
				body: JSON.stringify(payload),
			});

			const data = await response.json().catch(() => ({}));

			if (!response.ok) {
				const detail = data.detail || `HTTP ${response.status}`;
				throw new Error(detail);
			}

			this.sessionId = data.session_id || this.sessionId;
			this.saveSettings();
			this.appendMessage(data.text || 'Resposta vazia do backend.', 'assistant', this.formatNow());
			this.flashHealth('healthy', 'online');
		} catch (error) {
			this.appendMessage(`Falha ao chamar a API: ${error.message}`, 'assistant', 'erro');
			this.flashHealth('error', 'offline');
		} finally {
			this.toggleTyping(false);
			this.renderSession();
			this.persistHistory();
		}
	}

	appendMessage(text, role, meta) {
		const article = document.createElement('article');
		article.className = `message ${role === 'user' ? 'user-message' : 'assistant-message'}`;

		const avatar = document.createElement('div');
		avatar.className = 'avatar';
		avatar.textContent = role === 'user' ? 'EU' : 'AI';

		const bubbleWrap = document.createElement('div');
		bubbleWrap.className = 'bubble-wrap';

		const bubble = document.createElement('p');
		bubble.className = 'bubble';
		bubble.textContent = text;

		const metaTag = document.createElement('span');
		metaTag.className = 'message-meta';
		metaTag.textContent = meta || '';

		bubbleWrap.appendChild(bubble);
		bubbleWrap.appendChild(metaTag);
		article.appendChild(avatar);
		article.appendChild(bubbleWrap);

		this.chatMessages.appendChild(article);
		this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
	}

	toggleTyping(isVisible) {
		this.typingIndicator.classList.toggle('hidden', !isVisible);
		if (isVisible) {
			this.chatMessages.scrollTop = this.chatMessages.scrollHeight;
		}
	}

	clearChat() {
		this.sessionId = '';
		this.renderSession();
		this.chatMessages.innerHTML = '';
		this.appendMessage(
			'Historico limpo. A proxima mensagem vai iniciar uma nova sessao no backend.',
			'assistant',
			'sistema'
		);
		this.saveSettings();
		this.persistHistory();
	}

	async checkHealth() {
		const apiUrl = this.apiUrlInput.value.trim().replace(/\/$/, '');
		if (!apiUrl) {
			this.flashHealth('error', 'sem url');
			return;
		}

		this.flashHealth('pending', 'testando');

		try {
			const response = await fetch(`${apiUrl}/health`);
			if (!response.ok) {
				throw new Error(`HTTP ${response.status}`);
			}

			this.flashHealth('healthy', 'online');
		} catch (error) {
			console.warn('Health check falhou:', error);
			this.flashHealth('error', 'offline');
		}
	}

	flashHealth(state, label) {
		this.healthBadge.className = `health-badge ${state}`;
		this.healthBadge.textContent = label;
	}

	formatNow() {
		return new Date().toLocaleTimeString('pt-BR', {
			hour: '2-digit',
			minute: '2-digit',
		});
	}
}

document.addEventListener('DOMContentLoaded', () => {
	window.multiTenantChatUI = new MultiTenantChatUI();
});
