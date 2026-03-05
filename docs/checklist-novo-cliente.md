# Checklist de Levantamento — Novo Cliente

> Preencha este documento **antes** de escrever qualquer linha de código.  
> Cada item em aberto vira um bloqueio na implementação.

---

## 1. Identidade do Cliente

- [ ] **Nome oficial** da empresa (ex: "ACME Ltda")
- [ ] **Slug** para uso interno — minúsculo, sem espaços (ex: `acme`)
- [ ] **Idioma principal** dos usuários finais (pt-BR, en-US, es…)
- [ ] **Tom de voz desejado** — formal, informal, técnico, amigável?
- [ ] **Nome do assistente virtual** (se o cliente quiser personalizar)

---

## 2. Escopo do Bot

- [ ] **O que o bot DEVE fazer?** (lista de casos de uso principais)
  - Ex: responder dúvidas de produto, abrir chamados, agendar reuniões…
- [ ] **O que o bot NÃO deve fazer?** (guard rails — evita constrangimentos)
  - Ex: não falar de concorrentes, não citar preços, não dar conselhos jurídicos
- [ ] **O que acontece quando o bot não sabe a resposta?** (fallback)
  - Escalar para humano? Exibir e-mail/telefone? Abrir ticket?
- [ ] **Existe base de conhecimento?** (FAQs, PDFs, documentação técnica)
  - Se sim → habilitar RAG no config

---

## 3. Canais

Para cada canal que o cliente quer usar, colete:

### Web Chat
- [ ] O cliente tem site onde o widget será embutido? (URL)
- [ ] Precisa de autenticação do usuário antes do chat?

### WhatsApp (Twilio)
- [ ] Número de WhatsApp Business aprovado?
- [ ] `TWILIO_ACCOUNT_SID`
- [ ] `TWILIO_AUTH_TOKEN`
- [ ] `TWILIO_WHATSAPP_NUMBER` (formato: `whatsapp:+55119...`)

### Telegram
- [ ] Nome do bot criado no BotFather?
- [ ] `TELEGRAM_BOT_TOKEN`

### Slack
- [ ] Workspace Slack do cliente?
- [ ] `SLACK_BOT_TOKEN` (xoxb-...)
- [ ] `SLACK_SIGNING_SECRET`

---

## 4. LLM / Inteligência

- [ ] **Qual provedor?** OpenAI / Azure OpenAI / Ollama (offline)
- [ ] **Qual modelo?**
  - `gpt-4o-mini` → barato, rápido, bom para FAQ
  - `gpt-4o` → mais inteligente, fluxos complexos, custo maior
- [ ] **Quem paga pela API?** Cliente usa a própria chave ou a sua?
  - Se cliente: coletar `OPENAI_API_KEY` (ou credenciais Azure)
  - Se sua conta: separar billing por projeto no OpenAI dashboard
- [ ] **Limite de tokens por resposta?** (padrão: 512 para respostas curtas)
- [ ] **Temperatura?** (0.3 = mais preciso / 0.8 = mais criativo)

---

## 5. Infraestrutura e Deploy

- [ ] **Onde vai rodar?**
  - VPS própria (ex: DigitalOcean, Hetzner)
  - Cloud gerenciada (AWS ECS, Google Cloud Run, Azure Container Apps)
  - Servidor do cliente
- [ ] **Domínio/URL base** para os webhooks (ex: `https://bot.acme.com.br`)
  - Necessário para configurar Telegram, WhatsApp, Slack
- [ ] **Banco de dados** já existe ou precisa provisionar?
  - SQLite só para testes locais — PostgreSQL para produção
- [ ] **SSL/TLS** configurado? (obrigatório para webhooks)
- [ ] **Quem faz a manutenção pós-entrega?** Você ou o cliente?

---

## 6. Integrações Externas (se houver)

- [ ] **CRM** (HubSpot, Salesforce, RD Station…)?
  - URL do webhook ou API key
- [ ] **Helpdesk / ticketing** (Zendesk, Freshdesk, Jira…)?
- [ ] **ERP / sistema interno** para consulta de dados em tempo real?
- [ ] **Base de conhecimento** (Notion, Confluence, SharePoint, PDFs)?
  - Formato dos arquivos e frequência de atualização

---

## 7. Segurança e Compliance

- [ ] **Dados sensíveis** passarão pelo bot? (CPF, dados de saúde, financeiros)
  - Se sim → verificar se OpenAI/Azure permite (Data Processing Agreement)
- [ ] **LGPD**: cliente precisa de aviso de coleta de dados no chat?
- [ ] **Autenticação** dos usuários é necessária antes de responder?
- [ ] **Retenção de histórico** de conversas — por quanto tempo guardar?

---

## 8. Aceitação e Testes

- [ ] **Quem valida o prompt?** (geralmente o responsável de marketing/produto)
- [ ] **Quais frases de teste obrigatórias** o cliente quer ver funcionando?
- [ ] **Critério de "pronto"** — o que precisa acontecer para fazer o go-live?
- [ ] **Ambiente de homologação** separado ou testa direto em produção?

---

## Resumo Rápido — O Mínimo para Começar

Se o cliente não tiver tudo acima, você precisa **pelo menos** disto:

| Item | Por quê é bloqueante |
|------|----------------------|
| Slug + Nome oficial | Cria o pacote `customers/<slug>/` |
| Descrição do escopo (2–3 parágrafos) | Vira o system prompt |
| Chave de API do LLM | Sem isso o bot não responde |
| Canal + credenciais de 1 canal | Sem isso não tem como testar |
| URL pública com SSL | Necessária para webhooks externos |
