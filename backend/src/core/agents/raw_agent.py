# =============================================================================
# AGENTE SEM FRAMEWORK — CHAMADAS DIRETAS À API
# RAW AGENT — DIRECT API CALLS (no framework)
# =============================================================================
#
# Quando usar / When to use:
#   - Controle total sobre o loop de raciocínio / Full control over reasoning loop
#   - Sem dependências externas de framework / No external framework dependencies
#   - Ideal para entender como os agentes funcionam por baixo dos panos
#   - Ideal for understanding how agents work under the hood
#
# Dependências necessárias / Required dependencies:
#   uv add openai          → OpenAI-compatible APIs (OpenAI, Groq, Ollama, Azure)
#   uv add anthropic       → Anthropic Claude API
#   uv add httpx           → Para chamadas HTTP manuais / For manual HTTP calls
#
# =============================================================================


# -----------------------------------------------------------------------------
# 1. ESTRUTURA BÁSICA DO LOOP REACT
#    BASIC REACT LOOP STRUCTURE
# -----------------------------------------------------------------------------

# Um agente ReAct (Reason + Act) segue este ciclo:
# A ReAct agent follows this cycle:
#
#   Passo 1 / Step 1:
#     Enviar mensagem do usuário + lista de tools ao LLM
#     Send user message + list of tools to LLM
#
#   Passo 2 / Step 2:
#     LLM decide: responder diretamente OU chamar uma tool
#     LLM decides: respond directly OR call a tool
#
#   Passo 3 / Step 3 (se/if tool_call):
#     Executar a função localmente e devolver resultado ao LLM
#     Execute the function locally and return result to LLM
#
#   Passo 4 / Step 4:
#     Repetir até LLM gerar resposta final ou atingir max_steps
#     Repeat until LLM generates final response or max_steps reached


# -----------------------------------------------------------------------------
# 2. DEFINIÇÃO DE TOOLS (FUNCTION CALLING)
#    TOOL DEFINITION (FUNCTION CALLING)
# -----------------------------------------------------------------------------

# Cada tool precisa de:  / Each tool needs:
#   - name: str             → identificador snake_case que o LLM vai chamar
#   - description: str      → linguagem natural; LLM lê isso para decidir quando usar
#   - parameters: dict      → JSON Schema dos argumentos
#   - fn: async callable    → função Python que executa a lógica real

# Exemplo de schema OpenAI / OpenAI schema example:
#
# tools = [
#     {
#         "type": "function",
#         "function": {
#             "name": "buscar_pedido",
#             "description": "Busca o status de um pedido pelo número. / Fetches order status by number.",
#             "parameters": {
#                 "type": "object",
#                 "properties": {
#                     "numero_pedido": {
#                         "type": "string",
#                         "description": "Número do pedido, ex: PED-12345 / Order number, e.g. PED-12345"
#                     }
#                 },
#                 "required": ["numero_pedido"],
#             },
#         },
#     }
# ]


# -----------------------------------------------------------------------------
# 3. IMPLEMENTAÇÃO DO LOOP (OPENAI / GROQ / OLLAMA)
#    LOOP IMPLEMENTATION (OPENAI / GROQ / OLLAMA)
# -----------------------------------------------------------------------------

# import json
# import openai
#
# client = openai.AsyncOpenAI(api_key="...")
#
# async def run_agent(user_message: str, tools: list[dict], tool_fns: dict) -> str:
#     """
#     Executa o loop ReAct e retorna a resposta final.
#     Runs the ReAct loop and returns the final response.
#     """
#
#     messages = [{"role": "user", "content": user_message}]
#     MAX_STEPS = 5
#
#     for step in range(MAX_STEPS):
#         # Chama o LLM com a lista de tools disponíveis
#         # Call LLM with the list of available tools
#         response = await client.chat.completions.create(
#             model="gpt-4o-mini",
#             messages=messages,
#             tools=tools,
#             tool_choice="auto",   # "auto" | "none" | {"type": "function", "function": {"name": "..."}}
#         )
#
#         choice = response.choices[0]
#
#         # Verificar se o LLM quer chamar uma tool ou respondeu diretamente
#         # Check if LLM wants to call a tool or responded directly
#         if choice.finish_reason == "tool_calls":
#             # Adicionar resposta do assistente ao histórico
#             # Add assistant response to history
#             messages.append(choice.message.model_dump())
#
#             # Executar cada tool call e devolver resultado
#             # Execute each tool call and return result
#             for tool_call in choice.message.tool_calls:
#                 fn_name = tool_call.function.name
#                 fn_args = json.loads(tool_call.function.arguments)
#
#                 # Executar a função Python correspondente
#                 # Execute the corresponding Python function
#                 result = await tool_fns[fn_name](**fn_args)
#
#                 # Devolver resultado ao LLM como mensagem de role="tool"
#                 # Return result to LLM as role="tool" message
#                 messages.append({
#                     "role": "tool",
#                     "tool_call_id": tool_call.id,
#                     "content": str(result),
#                 })
#
#         elif choice.finish_reason == "stop":
#             # LLM gerou resposta final / LLM generated final response
#             return choice.message.content
#
#     return "Número máximo de iterações atingido. / Maximum iterations reached."


# -----------------------------------------------------------------------------
# 4. IMPLEMENTAÇÃO COM ANTHROPIC (CLAUDE)
#    IMPLEMENTATION WITH ANTHROPIC (CLAUDE)
# -----------------------------------------------------------------------------

# import anthropic
#
# client = anthropic.AsyncAnthropic(api_key="...")
#
# # Tools no formato Anthropic / Tools in Anthropic format
# tools = [
#     {
#         "name": "buscar_pedido",
#         "description": "Busca o status de um pedido. / Fetches order status.",
#         "input_schema": {
#             "type": "object",
#             "properties": {
#                 "numero_pedido": {"type": "string"}
#             },
#             "required": ["numero_pedido"],
#         },
#     }
# ]
#
# async def run_claude_agent(user_message: str) -> str:
#     messages = [{"role": "user", "content": user_message}]
#
#     for _ in range(5):
#         response = await client.messages.create(
#             model="claude-opus-4-6",
#             max_tokens=1024,
#             tools=tools,
#             messages=messages,
#         )
#
#         if response.stop_reason == "tool_use":
#             messages.append({"role": "assistant", "content": response.content})
#             tool_results = []
#
#             for block in response.content:
#                 if block.type == "tool_use":
#                     result = await tool_fns[block.name](**block.input)
#                     tool_results.append({
#                         "type": "tool_result",
#                         "tool_use_id": block.id,
#                         "content": str(result),
#                     })
#
#             messages.append({"role": "user", "content": tool_results})
#
#         elif response.stop_reason == "end_turn":
#             # Extrair texto da resposta / Extract text from response
#             for block in response.content:
#                 if hasattr(block, "text"):
#                     return block.text
#
#     return "Limite de iterações atingido. / Iteration limit reached."


# -----------------------------------------------------------------------------
# 5. DICAS GERAIS / GENERAL TIPS
# -----------------------------------------------------------------------------

# System prompt para agentes / System prompt for agents:
#   - Descreva as tools disponíveis em linguagem natural no system prompt
#   - Describe available tools in natural language in the system prompt
#   - Ex: "Você tem acesso a buscar_pedido(numero_pedido) e cancelar_pedido(numero_pedido)."
#   - Instrua o LLM a usar as tools antes de responder quando relevante
#   - Instruct LLM to use tools before responding when relevant

# Controle de loops / Loop control:
#   - Sempre defina max_steps para evitar loops infinitos / Always set max_steps to avoid infinite loops
#   - Logue cada step para depuração / Log each step for debugging
#   - Considere timeout total / Consider total timeout

# Tratamento de erros / Error handling:
#   - Capture exceções das tool_fns e retorne mensagem de erro como string
#   - Catch tool_fn exceptions and return error message as string
#   - O LLM consegue comunicar erros ao usuário de forma amigável
#   - LLM can communicate errors to user in a friendly way

# Streaming / Streaming:
#   - OpenAI: client.chat.completions.create(stream=True)
#   - Anthropic: client.messages.stream(...)
#   - Yield tokens conforme chegam para experiência mais responsiva
#   - Yield tokens as they arrive for a more responsive experience
