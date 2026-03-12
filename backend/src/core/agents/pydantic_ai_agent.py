# =============================================================================
# AGENTE COM PYDANTICAI
# AGENT WITH PYDANTICAI
# =============================================================================
#
# O que é PydanticAI / What is PydanticAI:
#   PydanticAI é um framework para agentes com foco em type safety e
#   validação de dados via Pydantic. Integra nativamente com FastAPI e
#   é modelado para ser agnóstico de modelo (OpenAI, Anthropic, Gemini, Groq).
#
#   PydanticAI is an agent framework focused on type safety and data
#   validation via Pydantic. Natively integrates with FastAPI and is
#   model-agnostic (OpenAI, Anthropic, Gemini, Groq).
#
# Quando usar / When to use:
#   - Quando type safety e validação de output importam / When type safety and output validation matter
#   - Projetos já usando FastAPI + Pydantic / Projects already using FastAPI + Pydantic
#   - Extração de dados estruturados confiáveis / Reliable structured data extraction
#   - Agentes com dependências injetadas (DB, serviços) / Agents with injected dependencies (DB, services)
#   - Preferência por API pythônica e simples / Preference for Pythonic and simple API
#
# Dependências necessárias / Required dependencies:
#   uv add pydantic-ai                  → base / base
#   uv add pydantic-ai[openai]          → com OpenAI / with OpenAI
#   uv add pydantic-ai[anthropic]       → com Anthropic / with Anthropic
#   uv add pydantic-ai[groq]            → com Groq / with Groq
#   uv add pydantic-ai[vertexai]        → com Google Vertex AI / with Google Vertex AI
#
# =============================================================================


# -----------------------------------------------------------------------------
# 1. CONCEITOS FUNDAMENTAIS / FUNDAMENTAL CONCEPTS
# -----------------------------------------------------------------------------

# Agent:
#   Objeto central que define modelo, system prompt, tools e tipo de resposta.
#   Central object defining model, system prompt, tools, and response type.
#   agent = Agent(model, system_prompt=..., result_type=MinhaClasse)

# Result type:
#   O tipo genérico Agent[DepsType, ResultType] garante que a resposta
#   do agente seja validada pelo Pydantic automaticamente.
#   The generic type Agent[DepsType, ResultType] ensures the agent's
#   response is validated by Pydantic automatically.

# RunContext / Dependencies:
#   Mecanismo de injeção de dependências — passa DB, clientes HTTP,
#   configurações para dentro dos tools sem variáveis globais.
#   Dependency injection mechanism — passes DB, HTTP clients, config
#   into tools without global variables.

# Tool:
#   Função decorada com @agent.tool que o LLM pode chamar.
#   Function decorated with @agent.tool that LLM can call.
#   Recebe RunContext como primeiro argumento para acessar dependências.
#   Receives RunContext as first argument to access dependencies.


# -----------------------------------------------------------------------------
# 2. AGENTE BÁSICO COM RESPOSTA ESTRUTURADA
#    BASIC AGENT WITH STRUCTURED RESPONSE
# -----------------------------------------------------------------------------

# from pydantic import BaseModel, Field
# from pydantic_ai import Agent
# from pydantic_ai.models.openai import OpenAIModel
#
# # 2.1 Definir o schema de saída / Define output schema
# class RespostaSuporte(BaseModel):
#     resposta: str = Field(description="Texto para o usuário / Text for the user")
#     requer_escalonamento: bool = Field(description="Se deve transferir para humano / Whether to escalate to human")
#     categoria: str = Field(description="pedido | financeiro | tecnico | outro")
#
# # 2.2 Criar o agente / Create the agent
# model = OpenAIModel("gpt-4o-mini")
# agent: Agent[None, RespostaSuporte] = Agent(
#     model=model,
#     result_type=RespostaSuporte,
#     system_prompt=(
#         "Você é um assistente de suporte. Classifique e responda a solicitação. "
#         "You are a support assistant. Classify and answer the request."
#     ),
# )
#
# # 2.3 Executar / Run
# result = await agent.run("quero cancelar meu pedido PED-123")
# print(result.data.resposta)              # texto validado / validated text
# print(result.data.requer_escalonamento)  # bool garantido / guaranteed bool
# print(result.data.categoria)             # str validada / validated str


# -----------------------------------------------------------------------------
# 3. AGENTE COM TOOLS E DEPENDÊNCIAS
#    AGENT WITH TOOLS AND DEPENDENCIES
# -----------------------------------------------------------------------------

# from dataclasses import dataclass
# from pydantic_ai import Agent, RunContext
# from pydantic_ai.models.anthropic import AnthropicModel
#
# # 3.1 Definir dependências como dataclass / Define dependencies as dataclass
# @dataclass
# class Deps:
#     db_session: Any          # sessão do banco / database session
#     cliente_http: Any        # cliente HTTP / HTTP client
#     user_id: str             # usuário autenticado / authenticated user
#
# # 3.2 Criar o agente com tipo de deps / Create agent with deps type
# agent: Agent[Deps, str] = Agent(
#     model=AnthropicModel("claude-opus-4-6"),
#     deps_type=Deps,
#     result_type=str,
#     system_prompt="Agente de pedidos com acesso ao banco de dados. / Orders agent with database access.",
# )
#
# # 3.3 Registrar tools com acesso a deps / Register tools with deps access
# @agent.tool
# async def buscar_pedido(ctx: RunContext[Deps], numero_pedido: str) -> str:
#     """
#     Busca o status de um pedido no banco de dados.
#     Fetches order status from the database.
#     """
#     # ctx.deps acessa as dependências injetadas / ctx.deps accesses injected dependencies
#     order = await ctx.deps.db_session.get_order(numero_pedido)
#     if not order:
#         return f"Pedido {numero_pedido} não encontrado. / Order not found."
#     return f"Status: {order.status}, Entrega prevista: {order.estimated_delivery}"
#
# @agent.tool
# async def listar_pedidos_usuario(ctx: RunContext[Deps]) -> str:
#     """
#     Lista todos os pedidos do usuário atual.
#     Lists all orders for the current user.
#     """
#     orders = await ctx.deps.db_session.list_orders(ctx.deps.user_id)
#     return "\n".join(f"- {o.id}: {o.status}" for o in orders)
#
# # 3.4 Executar com dependências / Run with dependencies
# deps = Deps(db_session=db, cliente_http=http, user_id="user-123")
# result = await agent.run("liste meus pedidos", deps=deps)


# -----------------------------------------------------------------------------
# 4. SYSTEM PROMPT DINÂMICO / DYNAMIC SYSTEM PROMPT
# -----------------------------------------------------------------------------

# O system prompt pode ser uma função que recebe o contexto de execução.
# The system prompt can be a function that receives the run context.
#
# @agent.system_prompt
# async def build_system_prompt(ctx: RunContext[Deps]) -> str:
#     """
#     Constrói o system prompt dinamicamente com dados do usuário.
#     Builds the system prompt dynamically with user data.
#     """
#     user = await ctx.deps.db_session.get_user(ctx.deps.user_id)
#     return (
#         f"Você é um assistente de suporte para {user.nome}. "
#         f"O plano do cliente é: {user.plano}. "
#         f"You are a support assistant for {user.nome}. "
#         f"The client's plan is: {user.plano}."
#     )


# -----------------------------------------------------------------------------
# 5. CONVERSAS MULTI-TURNO / MULTI-TURN CONVERSATIONS
# -----------------------------------------------------------------------------

# PydanticAI mantém histórico via message_history.
# PydanticAI maintains history via message_history.
#
# from pydantic_ai.messages import ModelMessagesTypeAdapter
#
# # Primeiro turno / First turn
# result1 = await agent.run("oi, quero saber sobre meu pedido", deps=deps)
# history = result1.all_messages()   # salvar no banco / save to database
#
# # Segundo turno — passar histórico anterior / Second turn — pass previous history
# result2 = await agent.run(
#     "e qual a previsão de entrega?",
#     deps=deps,
#     message_history=history,        # contexto mantido / context maintained
# )
#
# # Serializar para salvar no banco / Serialize to save in database:
# json_bytes = ModelMessagesTypeAdapter.dump_json(history)
# # Deserializar ao recuperar / Deserialize when retrieving:
# history = ModelMessagesTypeAdapter.validate_json(json_bytes)


# -----------------------------------------------------------------------------
# 6. STREAMING / STREAMING
# -----------------------------------------------------------------------------

# async with agent.run_stream("descreva meu pedido", deps=deps) as stream:
#     async for token in stream.stream_text():
#         yield token   # transmitir token por token / stream token by token
#
# # Para resposta estruturada com streaming (parcial validado) / For streaming structured response:
# async with agent.run_stream("analise meu pedido", deps=deps) as stream:
#     async for partial_result in stream.stream():
#         # partial_result pode ser incompleto até o fim / partial_result may be incomplete until end
#         print(partial_result)
#     final = await stream.get_data()   # resultado completo validado / complete validated result


# -----------------------------------------------------------------------------
# 7. INTEGRAÇÃO COM FASTAPI / FASTAPI INTEGRATION
# -----------------------------------------------------------------------------

# PydanticAI se integra naturalmente com FastAPI.
# PydanticAI integrates naturally with FastAPI.
#
# from fastapi import FastAPI, Depends
# from pydantic import BaseModel
#
# app = FastAPI()
#
# class ChatRequest(BaseModel):
#     user_id: str
#     message: str
#
# @app.post("/chat")
# async def chat(req: ChatRequest, db=Depends(get_db)):
#     deps = Deps(db_session=db, user_id=req.user_id)
#     result = await agent.run(req.message, deps=deps)
#     return {"response": result.data}
#
# # Streaming via SSE / Streaming via SSE:
# from fastapi.responses import StreamingResponse
#
# @app.post("/chat/stream")
# async def chat_stream(req: ChatRequest, db=Depends(get_db)):
#     async def generate():
#         deps = Deps(db_session=db, user_id=req.user_id)
#         async with agent.run_stream(req.message, deps=deps) as stream:
#             async for token in stream.stream_text():
#                 yield f"data: {token}\n\n"
#     return StreamingResponse(generate(), media_type="text/event-stream")


# -----------------------------------------------------------------------------
# 8. MODELOS SUPORTADOS / SUPPORTED MODELS
# -----------------------------------------------------------------------------

# from pydantic_ai.models.openai import OpenAIModel
# from pydantic_ai.models.anthropic import AnthropicModel
# from pydantic_ai.models.groq import GroqModel
# from pydantic_ai.models.gemini import GeminiModel
# from pydantic_ai.models.vertexai import VertexAIModel
# from pydantic_ai.models.ollama import OllamaModel     # modelos locais / local models
# from pydantic_ai.models.test import TestModel         # testes sem API / tests without API
#
# Configuração via string também funciona / String config also works:
# agent = Agent("openai:gpt-4o-mini")
# agent = Agent("anthropic:claude-opus-4-6")
# agent = Agent("groq:llama-3.3-70b-versatile")
# agent = Agent("google-gla:gemini-2.0-flash")


# -----------------------------------------------------------------------------
# 9. DICAS E BOAS PRÁTICAS / TIPS AND BEST PRACTICES
# -----------------------------------------------------------------------------

# Testes sem chamadas reais de API / Testing without real API calls:
#   from pydantic_ai.models.test import TestModel
#   agent = Agent(TestModel(), result_type=str)
#   result = await agent.run("test")   # rápido e gratuito / fast and free

# Retry automático / Automatic retry:
#   Se a validação Pydantic falhar, PydanticAI envia o erro de volta ao LLM
#   para que ele corrija a resposta automaticamente (retries configuráveis).
#   If Pydantic validation fails, PydanticAI sends the error back to LLM
#   so it can correct its response automatically (configurable retries).
#   agent = Agent(model, result_type=MinhaClasse, retries=3)

# UsageLimits para controlar custos / UsageLimits to control costs:
#   from pydantic_ai import UsageLimits
#   result = await agent.run(msg, usage_limits=UsageLimits(request_limit=5, total_tokens_limit=10_000))

# Observabilidade / Observability:
#   PydanticAI se integra com Logfire (da equipe Pydantic) para tracing.
#   PydanticAI integrates with Logfire (from Pydantic team) for tracing.
#   import logfire; logfire.configure(); logfire.instrument_pydantic_ai()
