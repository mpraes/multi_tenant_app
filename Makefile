# Makefile — atalhos para tarefas comuns / Shortcuts for common tasks
# Uso / Usage: make <target>

RUN_DIR := .run

.PHONY: help install dev frontend run stop db-upgrade db-migrate test chat \
        config-show config-set config-reset docker

# Exibe os alvos disponíveis / Show available targets
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}' | sort

# ── Setup ─────────────────────────────────────────────────────────────────────

install: ## Instala dependências (uv sync --extra dev)
	uv sync --extra dev

install-rag: ## Instala dependências com extras RAG
	uv sync --extra dev --extra rag

env: ## Copia .env.example para .env (só se não existir)
	@[ -f backend/.env ] && echo "backend/.env já existe." || \
		(cp backend/.env.example backend/.env && echo "backend/.env criado.")

# ── Servidores / Servers ──────────────────────────────────────────────────────

dev: ## Sobe o backend em modo dev (porta 8000)
	cd backend && uv run uvicorn src.main:app --reload --port 8000

frontend: ## Sobe o frontend estático (porta 3000)
	cd frontend && uv run python serve.py

run: ## Sobe backend + frontend em background (portas 8000 e 3000)
	@mkdir -p $(RUN_DIR)
	@cd backend && uv run uvicorn src.main:app --reload --port 8000 \
		> ../$(RUN_DIR)/backend.log 2>&1 & echo $$! > ../$(RUN_DIR)/backend.pid \
		&& echo "  Backend   iniciado (pid $$(cat ../$(RUN_DIR)/backend.pid)) → http://localhost:8000"
	@cd frontend && uv run python serve.py \
		> ../$(RUN_DIR)/frontend.log 2>&1 & echo $$! > ../$(RUN_DIR)/frontend.pid \
		&& echo "  Frontend  iniciado (pid $$(cat ../$(RUN_DIR)/frontend.pid)) → http://127.0.0.1:3000"
	@echo ""
	@echo "  Logs:  tail -f $(RUN_DIR)/backend.log"
	@echo "         tail -f $(RUN_DIR)/frontend.log"
	@echo "  Para encerrar: make stop"

stop: ## Para backend e frontend iniciados com make run
	@if [ -f $(RUN_DIR)/backend.pid ]; then \
		kill $$(cat $(RUN_DIR)/backend.pid) 2>/dev/null \
			&& echo "  Backend  parado." || echo "  Backend  já estava parado."; \
		rm -f $(RUN_DIR)/backend.pid; \
	else echo "  backend.pid não encontrado — nada a fazer."; fi
	@if [ -f $(RUN_DIR)/frontend.pid ]; then \
		kill $$(cat $(RUN_DIR)/frontend.pid) 2>/dev/null \
			&& echo "  Frontend parado." || echo "  Frontend já estava parado."; \
		rm -f $(RUN_DIR)/frontend.pid; \
	else echo "  frontend.pid não encontrado — nada a fazer."; fi

docker: ## Sobe tudo via Docker Compose
	docker-compose -f infra/docker/docker-compose.yml up --build

# ── Banco de dados / Database ─────────────────────────────────────────────────

db-upgrade: ## Aplica migrações pendentes
	cd backend && uv run alembic upgrade head

db-migrate: ## Gera nova migração (uso: make db-migrate m="descricao")
	@[ -n "$(m)" ] || { echo "Uso: make db-migrate m=\"descricao da migracao\""; exit 1; }
	cd backend && uv run alembic revision --autogenerate -m "$(m)"

# ── Testes / Tests ────────────────────────────────────────────────────────────

test: ## Roda todos os testes
	uv run pytest backend/tests/ -v --asyncio-mode=auto

test-file: ## Roda um arquivo de teste (uso: make test-file f=test_engine.py)
	uv run pytest backend/tests/$(f) -v --asyncio-mode=auto

# ── Chat API (smoke test) ─────────────────────────────────────────────────────

chat: ## Envia mensagem de teste para POST /chat
	curl -s -X POST http://localhost:8000/chat \
		-H "Content-Type: application/json" \
		-d '{"user_id": "test-user", "text": "ola"}' | python3 -m json.tool

health: ## Verifica GET /health
	curl -s http://localhost:8000/health | python3 -m json.tool

# ── Config do bot / Bot config ────────────────────────────────────────────────

config-show: ## Exibe a configuração atual do bot
	cd backend && uv run python -m src.cli show

config-set: ## Define um campo (uso: make config-set k=name v="Meu Bot")
	@[ -n "$(k)" ] || { echo "Uso: make config-set k=<campo> v=<valor>"; \
		echo "Campos: name system_prompt llm_provider llm_model llm_temperature llm_max_tokens rag_enabled history_window"; \
		exit 1; }
	cd backend && uv run python -m src.cli set $(k) "$(v)"

config-reset: ## Remove config.json (volta aos defaults)
	cd backend && uv run python -m src.cli reset
