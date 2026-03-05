# Guia de Implementação — Passo a Passo

> Para usar após preencher o `checklist-novo-cliente.md`.  
> Tempo estimado do zero ao go-live: **2–4 horas** por cliente simples.

---

## Pré-requisitos (faça uma vez, vale para todos os clientes)

```bash
# Clone o repositório base
git clone <url-do-repo> multi_tenant_app
cd multi_tenant_app

# Crie o virtualenv e instale as dependências
python -m venv .venv && source .venv/bin/activate
pip install -r backend/requirements.txt

# Configure o ambiente base
cp backend/.env.example backend/.env
```

---

## Passo 1 — Criar o pacote do cliente

Execute o script de scaffolding com o slug e nome do cliente:

```bash
python scripts/new_client.py <slug> "<Nome do Cliente>"

# Exemplo:
python scripts/new_client.py acme "ACME Ltda"
```

**O que é criado automaticamente:**

```
backend/src/customers/acme/
├── __init__.py     # declaração do pacote
├── config.py       # configurações do tenant
├── prompts.py      # system prompt
└── flows.py        # atalhos de palavras-chave
```

> O servidor detecta o novo pacote automaticamente no próximo restart.  
> Nenhuma alteração no código principal é necessária.

---

## Passo 2 — Escrever o system prompt

Abra `backend/src/customers/<slug>/prompts.py` e preencha `SYSTEM_PROMPT`.

Este é o passo mais importante — define a personalidade e o escopo do bot.

**Template comentado:**

```python
SYSTEM_PROMPT = """\
Você é o assistente virtual da <Nome do Cliente>.

# Tom de voz
<Descreva: formal/informal, objetivo/empático, técnico/simples>

# O que você pode ajudar
- <Caso de uso 1>
- <Caso de uso 2>
- <Caso de uso 3>

# O que está fora do escopo
- NÃO discuta <assunto proibido 1>.
- NÃO forneça <assunto proibido 2>.

# Quando não souber a resposta
Diga claramente que não sabe e oriente o usuário a entrar em contato
pelo e-mail <email> ou pelo telefone <telefone>.

Sempre responda no mesmo idioma em que o usuário escrever.
"""
```

**Dica:** teste o prompt no ChatGPT antes de colocar no código — é mais rápido para iterar.

---

## Passo 3 — Configurar o tenant

Abra `backend/src/customers/<slug>/config.py` e ajuste cada campo:

```python
CONFIG = TenantConfig(
    slug="acme",
    name="ACME Ltda",

    # Canais que o cliente vai usar
    enabled_channels=["web_chat", "telegram"],

    # LLM
    llm_provider="openai",       # openai | azure_openai | ollama
    llm_model="gpt-4o-mini",     # barato: gpt-4o-mini | complexo: gpt-4o
    llm_temperature=0.6,         # 0.3 = preciso | 0.8 = criativo
    llm_max_tokens=512,

    system_prompt_override=SYSTEM_PROMPT,
    flows=ACME_FLOWS,

    rag_enabled=False,           # True se tiver base de conhecimento
    history_window=8,            # quantos turnos guardar no contexto

    extra={
        "support_email": "suporte@acme.com.br",
        "business_hours": "Seg–Sex 9h–18h",
    },
)
```

---

## Passo 4 — Adicionar fluxos específicos (opcional)

Abra `backend/src/customers/<slug>/flows.py` e adicione handlers para
intenções frequentes do cliente. Isso evita chamar o LLM desnecessariamente
para respostas que são sempre iguais.

```python
async def handle_preco(ctx: ConversationContext) -> str:
    return (
        "Para informações sobre preços, fale com nossa equipe comercial:\n"
        "📧 vendas@acme.com.br\n"
        "📞 (11) 9999-9999"
    )

async def handle_horario(ctx: ConversationContext) -> str:
    return "Nosso atendimento é de segunda a sexta, das 9h às 18h (horário de Brasília)."

FLOWS: dict = {
    "preço": handle_preco,
    "valor": handle_preco,
    "quanto custa": handle_preco,
    "horário": handle_horario,
    "atendimento": handle_horario,
}
```

> **Regra:** se a resposta é sempre a mesma, use um flow.  
> Se precisa de raciocínio ou contexto, deixa o LLM responder.

---

## Passo 5 — Configurar as variáveis de ambiente

Edite `backend/.env` com as credenciais do cliente:

```bash
# LLM (obrigatório)
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-proj-...

# Canais (preencha apenas os que forem usar)
TELEGRAM_BOT_TOKEN=1234567890:AAF...
TWILIO_ACCOUNT_SID=ACxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxx
TWILIO_WHATSAPP_NUMBER=whatsapp:+5511999999999

# Banco (SQLite para dev, PostgreSQL para produção)
DATABASE_URL=sqlite+aiosqlite:///./dev.db
```

> **Atenção:** cada cliente pode ter sua própria chave de API.  
> Considere um arquivo `.env.<slug>` por cliente e carregar o correto no deploy.

---

## Passo 6 — Testar localmente

**Suba o servidor:**

```bash
cd backend
uvicorn src.main:app --reload --port 8000
```

**Verifique se o tenant foi detectado:**

```bash
curl http://localhost:8000/tenants
# Deve retornar: [{"slug": "acme", "name": "ACME Ltda"}, ...]
```

**Envie uma mensagem de teste:**

```bash
curl -X POST http://localhost:8000/chat/acme \
  -H "Content-Type: application/json" \
  -d '{"user_id": "teste", "text": "olá"}'
```

**Teste os fluxos específicos:**

```bash
# Testa um flow keyword
curl -X POST http://localhost:8000/chat/acme \
  -H "Content-Type: application/json" \
  -d '{"user_id": "teste", "text": "qual o preço?"}'

# Testa o fallback (LLM livre)
curl -X POST http://localhost:8000/chat/acme \
  -H "Content-Type: application/json" \
  -d '{"user_id": "teste", "text": "como funciona o produto?"}'
```

---

## Passo 7 — Subir com Docker (staging / produção)

```bash
# A partir da raiz do projeto:
docker-compose -f infra/docker/docker-compose.yml up --build -d

# Verificar se está saudável:
curl http://localhost:8000/health
# {"status": "ok", "env": "development"}

# Ver logs em tempo real:
docker-compose -f infra/docker/docker-compose.yml logs -f backend
```

Para produção, altere no `.env`:

```bash
APP_ENV=production
DATABASE_URL=postgresql+asyncpg://user:senha@host:5432/chatbot
```

---

## Passo 8 — Configurar webhooks dos canais

Os canais externos (Telegram, WhatsApp, Slack) precisam de uma URL pública com SSL.
Use o domínio do cliente ou um subdomínio seu (ex: `https://bot.acme.com.br`).

### Telegram

```bash
curl "https://api.telegram.org/bot<TOKEN>/setWebhook" \
  -d "url=https://bot.acme.com.br/channels/telegram/<slug>"
```

> O endpoint Telegram ainda precisa ser implementado em `channels/telegram.py`.  
> A estrutura base já existe — implemente seguindo o mesmo padrão do `web_chat.py`.

### WhatsApp (Twilio)

No painel do Twilio → Messaging → WhatsApp Sandbox:
- **Webhook URL:** `https://bot.acme.com.br/channels/whatsapp/acme`
- **Method:** POST

### Slack

No painel do Slack App → Event Subscriptions:
- **Request URL:** `https://bot.acme.com.br/channels/slack/acme`

---

## Passo 9 — Rodar as migrações do banco (produção)

```bash
# Sempre que o schema mudar:
cd backend
alembic revision --autogenerate -m "describe change"
alembic upgrade head
```

> Em produção o Docker já roda `alembic upgrade head` antes de iniciar o servidor.  
> Veja `backend/Dockerfile` — linha `CMD`.

---

## Passo 10 — Checklist de go-live

Antes de passar a URL para o cliente:

- [ ] Todos os fluxos do checklist de levantamento foram testados?
- [ ] O bot responde corretamente em português (e no idioma configurado)?
- [ ] O fallback funciona sem travar ou dar erro 500?
- [ ] As credenciais de produção estão no `.env` correto (não as de dev)?
- [ ] `APP_ENV=production` está definido?
- [ ] `/docs` está desabilitado em produção? (acontece automaticamente com `APP_ENV=production`)
- [ ] O endpoint `/tenants` está protegido ou desabilitado? (remova em `main.py` se necessário)
- [ ] Logs estão sendo capturados em algum serviço (CloudWatch, Datadog, Loki…)?
- [ ] O cliente foi avisado sobre o custo estimado por mensagem (tokens)?

---

## Referência Rápida — Estrutura de Arquivos por Cliente

```
backend/src/customers/<slug>/
├── __init__.py      → não editar
├── config.py        → EDITAR: canais, modelo, extras        ← Passo 3
├── prompts.py       → EDITAR: system prompt                 ← Passo 2
└── flows.py         → EDITAR: respostas fixas por keyword   ← Passo 4
```

## Referência Rápida — Comandos do Dia a Dia

```bash
# Criar novo cliente
python scripts/new_client.py <slug> "<Nome>"

# Rodar local com reload
cd backend && uvicorn src.main:app --reload

# Rodar com Docker
docker-compose -f infra/docker/docker-compose.yml up --build

# Ver tenants carregados
curl http://localhost:8000/tenants

# Testar chat
curl -X POST http://localhost:8000/chat/<slug> \
  -H "Content-Type: application/json" \
  -d '{"user_id": "eu", "text": "olá"}'

# Criar migração de banco
cd backend && alembic revision --autogenerate -m "descrição"
alembic upgrade head
```
