# Multi-Tenant App

Estrutura principal de pastas do workspace:

```text
multi_tenant_app/
├── pyproject.toml
├── README.md
├── backend/
│   ├── pyproject.toml
│   ├── README.md
│   ├── requirements.txt
│   ├── setup.cfg
│   ├── examples/
│   │   ├── simple_console_bot/
│   │   │   └── main.py
│   │   └── whatsapp_bot/
│   │       ├── docker-compose.yml
│   │       └── main.py
│   ├── src/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── api/
│   │   ├── channels/
│   │   ├── config/
│   │   ├── core/
│   │   ├── customers/
│   │   ├── domain/
│   │   ├── llm/
│   │   ├── rag/
│   │   ├── storage/
│   │   └── utils/
│   ├── tests/
│   │   ├── test_channels/
│   │   ├── test_core/
│   │   └── test_llm/
│   └── ci/
├── docs/
├── frontend/
│   ├── public/
│   │   ├── app.js
│   │   ├── index.html
│   │   └── styles.css
│   └── tests/
├── infra/
│   ├── docker/
│   ├── k8s/
│   └── terraform/
├── logs/
└── scripts/
```

## Resumo rápido

- `backend/`: núcleo do chatbot multi-tenant (canais, engine, domínio, LLM, storage e testes).
- `frontend/`: interface web estática e testes do frontend.
- `infra/`: artefatos de infraestrutura (Docker, Kubernetes e Terraform).
- `docs/`: documentação do projeto.
- `scripts/`: scripts utilitários de automação.
- `logs/`: saída de logs locais.

## Detalhe do `backend/src`

- `main.py`: ponto de entrada da aplicação backend.
- `api/`: endpoints e camada de exposição HTTP/API.
- `channels/`: adaptadores de entrada/saída por canal (Slack, Telegram, WhatsApp, Web Chat).
- `config/`: carregamento e centralização de configurações da aplicação.
- `core/`: engine principal, contexto, roteamento, middlewares e erros base.
- `customers/`: customizações por cliente/tenant (config, flows e prompts por cliente).
- `domain/`: regras de negócio padrão, fluxos e handlers genéricos.
- `llm/`: provedores e interfaces de integração com modelos de linguagem.
- `rag/`: componentes de recuperação de contexto/conhecimento (RAG).
- `storage/`: persistência em cache, arquivos, NoSQL e SQL.
- `utils/`: utilitários compartilhados (IDs, tempo, logging, etc.).
