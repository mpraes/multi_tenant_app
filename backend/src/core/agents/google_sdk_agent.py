# =============================================================================
# AGENTE COM GOOGLE GENERATIVE AI / GEMINI SDK
# AGENT WITH GOOGLE GENERATIVE AI / GEMINI SDK
# =============================================================================
#
# O que é / What is it:
#   O Google oferece dois SDKs para trabalhar com Gemini:
#   Google offers two SDKs for working with Gemini:
#
#   1. google-generativeai (SDK clássico, mais simples)
#      Classic SDK, simpler. Pacote: google-generativeai
#
#   2. google-genai (SDK novo, recomendado, suporta Gemini 2.x)
#      New SDK, recommended, supports Gemini 2.x. Pacote: google-genai
#
#   3. Google Agent Development Kit (ADK) — framework completo para agentes
#      Full-featured agent framework. Pacote: google-adk
#      Análogo ao LangGraph, mas específico para o ecossistema Google.
#      Analogous to LangGraph but specific to the Google ecosystem.
#
# Quando usar / When to use:
#   - Quando o cliente usa Google Cloud / When client uses Google Cloud
#   - Para integrar com Vertex AI, Google Search, Google Maps / Integrate with Vertex AI, etc.
#   - Modelos multimodais (texto, imagem, áudio, vídeo) / Multimodal models (text, image, audio, video)
#   - Contextos muito longos (Gemini suporta até 2M tokens) / Very long context (Gemini supports up to 2M tokens)
#   - Grounding com Google Search nativo / Grounding with native Google Search
#
# Dependências necessárias / Required dependencies:
#   uv add google-genai                → SDK novo (recomendado) / New SDK (recommended)
#   uv add google-generativeai         → SDK clássico / Classic SDK
#   uv add google-adk                  → Agent Development Kit (ADK)
#
# Autenticação / Authentication:
#   GOOGLE_API_KEY=...    → API Key do AI Studio / AI Studio API Key
#   GOOGLE_CLOUD_PROJECT= → Vertex AI (usa credenciais gcloud) / Vertex AI (uses gcloud credentials)
#
# =============================================================================


# -----------------------------------------------------------------------------
# 1. SDK NOVO (google-genai) — RECOMENDADO
#    NEW SDK (google-genai) — RECOMMENDED
# -----------------------------------------------------------------------------

# from google import genai
# from google.genai import types
#
# client = genai.Client(api_key="GOOGLE_API_KEY")
#
# # 1.1 Chat simples / Simple chat
# response = await client.aio.models.generate_content(
#     model="gemini-2.0-flash",
#     contents="Olá! Como posso ajudar? / Hello! How can I help?",
#     config=types.GenerateContentConfig(
#         system_instruction="Você é um assistente de suporte. / You are a support assistant.",
#         temperature=0.3,
#         max_output_tokens=1024,
#     ),
# )
# print(response.text)
#
# # 1.2 Chat multi-turno / Multi-turn chat
# chat = client.aio.chats.create(
#     model="gemini-2.0-flash",
#     config=types.GenerateContentConfig(
#         system_instruction="Responda de forma concisa. / Answer concisely."
#     ),
# )
# resp1 = await chat.send_message("Qual o status do pedido PED-123?")
# resp2 = await chat.send_message("E a previsão de entrega?")   # contexto mantido / context maintained


# -----------------------------------------------------------------------------
# 2. FUNCTION CALLING (TOOLS) COM O SDK NOVO
#    FUNCTION CALLING (TOOLS) WITH NEW SDK
# -----------------------------------------------------------------------------

# from google import genai
# from google.genai import types
#
# # 2.1 Definir funções Python / Define Python functions
# async def buscar_pedido(numero_pedido: str) -> dict:
#     """
#     Busca o status de um pedido pelo número.
#     Fetches order status by number.
#     """
#     # Lógica real aqui / Real logic here
#     return {"status": "em_transito", "previsao": "2026-03-15"}
#
# # 2.2 Passar funções Python diretamente — o SDK gera o schema automaticamente
# #     Pass Python functions directly — SDK generates schema automatically
# config = types.GenerateContentConfig(
#     tools=[buscar_pedido],          # funções Python direto / Python functions directly
#     tool_config=types.ToolConfig(
#         function_calling_config=types.FunctionCallingConfig(
#             mode="AUTO"             # AUTO | ANY | NONE
#         )
#     ),
# )
#
# # 2.3 Loop automático de function calling / Automatic function calling loop
# # O SDK novo suporta execução automática de tools (agentic loop integrado)
# # The new SDK supports automatic tool execution (integrated agentic loop)
# response = await client.aio.models.generate_content(
#     model="gemini-2.0-flash",
#     contents="Qual o status do PED-456?",
#     config=config,
# )
# # response.text já contém a resposta final após executar as tools
# # response.text already contains final response after executing tools
#
# # 2.4 Loop manual (para mais controle) / Manual loop (for more control)
# # Verificar se há function calls / Check for function calls:
# for part in response.candidates[0].content.parts:
#     if part.function_call:
#         fn_name = part.function_call.name
#         fn_args = dict(part.function_call.args)
#         result = await tool_fns[fn_name](**fn_args)
#         # Enviar resultado de volta / Send result back:
#         # contents.append(types.Content(role="user", parts=[
#         #     types.Part(function_response=types.FunctionResponse(
#         #         name=fn_name, response={"result": result}
#         #     ))
#         # ]))


# -----------------------------------------------------------------------------
# 3. SAÍDA ESTRUTURADA / STRUCTURED OUTPUT
# -----------------------------------------------------------------------------

# Gemini suporta resposta em JSON Schema via response_schema.
# Gemini supports JSON Schema response via response_schema.
#
# from google.genai import types
# from pydantic import BaseModel
#
# class InfoPedido(BaseModel):
#     numero_pedido: str
#     acao: str    # "status" | "cancelar" | "alterar_endereco"
#     urgente: bool
#
# response = await client.aio.models.generate_content(
#     model="gemini-2.0-flash",
#     contents="cancelar urgente o pedido PED-789",
#     config=types.GenerateContentConfig(
#         response_mime_type="application/json",
#         response_schema=InfoPedido,   # Pydantic model direto / direct Pydantic model
#     ),
# )
# info = InfoPedido.model_validate_json(response.text)


# -----------------------------------------------------------------------------
# 4. MULTIMODAL — TEXTO + IMAGEM + ÁUDIO
#    MULTIMODAL — TEXT + IMAGE + AUDIO
# -----------------------------------------------------------------------------

# from google.genai import types
# import pathlib
#
# # 4.1 Analisar imagem local / Analyze local image
# response = await client.aio.models.generate_content(
#     model="gemini-2.0-flash",
#     contents=[
#         types.Part.from_bytes(
#             data=pathlib.Path("foto_produto.jpg").read_bytes(),
#             mime_type="image/jpeg",
#         ),
#         "Descreva os defeitos visíveis neste produto. / Describe visible defects.",
#     ],
# )
#
# # 4.2 Analisar imagem via URL / Analyze image via URL
# response = await client.aio.models.generate_content(
#     model="gemini-2.0-flash",
#     contents=[
#         types.Part.from_uri(
#             file_uri="https://exemplo.com/produto.jpg",
#             mime_type="image/jpeg",
#         ),
#         "O produto está danificado? / Is the product damaged?",
#     ],
# )
#
# # 4.3 Contexto longo — enviar PDF / Long context — send PDF
# response = await client.aio.models.generate_content(
#     model="gemini-2.0-flash",
#     contents=[
#         types.Part.from_bytes(
#             data=pathlib.Path("contrato.pdf").read_bytes(),
#             mime_type="application/pdf",
#         ),
#         "Resuma as cláusulas de cancelamento. / Summarize cancellation clauses.",
#     ],
# )


# -----------------------------------------------------------------------------
# 5. GROUNDING COM GOOGLE SEARCH
#    GROUNDING WITH GOOGLE SEARCH
# -----------------------------------------------------------------------------

# Gemini pode buscar informações atualizadas no Google Search automaticamente.
# Gemini can fetch up-to-date information from Google Search automatically.
#
# from google.genai import types
#
# response = await client.aio.models.generate_content(
#     model="gemini-2.0-flash",
#     contents="Qual o preço atual do dólar? / What is the current dollar price?",
#     config=types.GenerateContentConfig(
#         tools=[types.Tool(google_search=types.GoogleSearch())],
#     ),
# )
# # response.candidates[0].grounding_metadata contém as fontes usadas
# # response.candidates[0].grounding_metadata contains the sources used


# -----------------------------------------------------------------------------
# 6. GOOGLE AGENT DEVELOPMENT KIT (ADK)
#    GOOGLE AGENT DEVELOPMENT KIT (ADK)
# -----------------------------------------------------------------------------

# ADK é o framework da Google para agentes complexos, análogo ao LangGraph.
# ADK is Google's framework for complex agents, analogous to LangGraph.
#
# from google.adk.agents import Agent, SequentialAgent, ParallelAgent
# from google.adk.tools import FunctionTool
# from google.adk.runners import InMemoryRunner
#
# # 6.1 Definir uma tool / Define a tool
# async def buscar_pedido(numero_pedido: str) -> dict:
#     """Busca o status de um pedido. / Fetches order status."""
#     return {"status": "em_transito"}
#
# # 6.2 Criar o agente raiz / Create the root agent
# root_agent = Agent(
#     name="agente_suporte",
#     model="gemini-2.0-flash",
#     description="Agente de suporte ao cliente. / Customer support agent.",
#     instruction="Responda perguntas sobre pedidos usando as tools disponíveis.",
#     tools=[FunctionTool(func=buscar_pedido)],
# )
#
# # 6.3 Executar via runner / Run via runner
# runner = InMemoryRunner(agent=root_agent, app_name="suporte")
# session = await runner.session_service.create_session(app_name="suporte", user_id="user-1")
#
# from google.adk.types import Content, Part
# response = runner.run(
#     user_id="user-1",
#     session_id=session.id,
#     new_message=Content(parts=[Part(text="qual o status do PED-123?")], role="user"),
# )
# async for event in response:
#     if event.is_final_response():
#         print(event.content.parts[0].text)
#
# # 6.4 Agentes especializados compostos / Composed specialized agents
# # SequentialAgent: executa sub-agentes em sequência
# # SequentialAgent: executes sub-agents in sequence
# pipeline = SequentialAgent(
#     name="pipeline_suporte",
#     sub_agents=[classificador_agent, resposta_agent, escalonamento_agent],
# )
#
# # ParallelAgent: executa sub-agentes em paralelo e combina resultados
# # ParallelAgent: executes sub-agents in parallel and combines results
# paralelo = ParallelAgent(
#     name="pesquisa_paralela",
#     sub_agents=[busca_pedido_agent, busca_historico_agent],
# )


# -----------------------------------------------------------------------------
# 7. STREAMING / STREAMING
# -----------------------------------------------------------------------------

# from google import genai
#
# # Streaming de texto / Text streaming
# async for chunk in await client.aio.models.generate_content_stream(
#     model="gemini-2.0-flash",
#     contents="Explique o processo de devolução.",
# ):
#     if chunk.text:
#         yield chunk.text   # token por token / token by token


# -----------------------------------------------------------------------------
# 8. VERTEX AI (PRODUÇÃO NO GOOGLE CLOUD)
#    VERTEX AI (PRODUCTION ON GOOGLE CLOUD)
# -----------------------------------------------------------------------------

# Para produção no GCP, use Vertex AI ao invés do AI Studio.
# For production on GCP, use Vertex AI instead of AI Studio.
#
# from google import genai
#
# client = genai.Client(
#     vertexai=True,
#     project="meu-projeto-gcp",     # GOOGLE_CLOUD_PROJECT
#     location="us-central1",        # região / region
# )
# # Mesma API do SDK novo / Same API as new SDK
# response = await client.aio.models.generate_content(
#     model="gemini-2.0-flash-001",   # modelos Vertex têm sufixo de versão
#     contents="Olá!",
# )


# -----------------------------------------------------------------------------
# 9. DICAS E BOAS PRÁTICAS / TIPS AND BEST PRACTICES
# -----------------------------------------------------------------------------

# Modelos disponíveis / Available models:
#   gemini-2.0-flash         → rápido e econômico, ideal para produção / fast and cheap, ideal for production
#   gemini-2.0-flash-lite    → mais econômico ainda / even cheaper
#   gemini-2.5-pro           → mais capaz, contexto longo / most capable, long context
#   gemini-2.5-flash         → equilíbrio custo/capacidade / cost/capability balance
#
# Limites de contexto / Context limits:
#   gemini-2.0-flash: 1M tokens
#   gemini-2.5-pro: 2M tokens
#   Ideal para processar documentos longos sem chunking / Ideal for long docs without chunking
#
# Safety settings / Safety settings:
#   config=types.GenerateContentConfig(
#       safety_settings=[
#           types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="BLOCK_NONE"),
#       ]
#   )
#
# Caching de contexto / Context caching:
#   Para prompts longos repetidos, use cached_content para reduzir custos.
#   For repeated long prompts, use cached_content to reduce costs.
#   cache = await client.aio.caches.create(model=..., contents=[doc_longo], ttl="3600s")
#   config = types.GenerateContentConfig(cached_content=cache.name)
