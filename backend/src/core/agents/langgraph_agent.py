# =============================================================================
# AGENTE COM LANGGRAPH
# AGENT WITH LANGGRAPH
# =============================================================================
#
# O que é LangGraph / What is LangGraph:
#   LangGraph modela o agente como um grafo de estados onde cada nó é
#   uma etapa de processamento (LLM, tool, roteamento) e as arestas
#   definem o fluxo de controle condicional.
#
#   LangGraph models the agent as a state graph where each node is a
#   processing step (LLM, tool, routing) and edges define conditional
#   control flow.
#
# Quando usar / When to use:
#   - Fluxos multi-etapa com ramificação condicional / Multi-step flows with conditional branching
#   - Agentes com memória persistente entre execuções / Agents with persistent memory across runs
#   - Pipelines paralelos (fan-out / fan-in) / Parallel pipelines (fan-out / fan-in)
#   - Sistemas multi-agente com supervisores / Multi-agent systems with supervisors
#   - Quando precisar de checkpointing / rollback / When you need checkpointing / rollback
#
# Dependências necessárias / Required dependencies:
#   uv add langgraph langchain-openai   → com OpenAI / with OpenAI
#   uv add langgraph langchain-anthropic → com Anthropic / with Anthropic
#
# =============================================================================


# -----------------------------------------------------------------------------
# 1. CONCEITOS FUNDAMENTAIS / FUNDAMENTAL CONCEPTS
# -----------------------------------------------------------------------------

# State (Estado):
#   TypedDict que representa TODOS os dados do agente em um dado momento.
#   TypedDict representing ALL agent data at a given moment.
#   Cada nó lê o estado, processa e retorna um dict com os campos atualizados.
#   Each node reads the state, processes, and returns a dict with updated fields.
#
#   Exemplo / Example:
#   class AgentState(TypedDict):
#       messages: Annotated[list[AnyMessage], add_messages]   # acumula / accumulates
#       numero_pedido: str                                     # dado de domínio / domain data
#       etapa_atual: str                                       # controle de fluxo / flow control

# Node (Nó):
#   Função Python que recebe o estado e retorna delta de atualização.
#   Python function that receives state and returns update delta.
#   async def meu_no(state: AgentState) -> dict: ...

# Edge (Aresta):
#   Conexão entre nós. Pode ser incondicional ou condicional (via função).
#   Connection between nodes. Can be unconditional or conditional (via function).
#   Aresta condicional escolhe o próximo nó com base no estado atual.
#   Conditional edge chooses the next node based on current state.

# START / END:
#   Nós especiais que marcam entrada e saída do grafo.
#   Special nodes marking entry and exit of the graph.


# -----------------------------------------------------------------------------
# 2. CRIANDO O GRAFO BÁSICO / CREATING THE BASIC GRAPH
# -----------------------------------------------------------------------------

# from typing import Annotated
# from typing_extensions import TypedDict
# from langgraph.graph import StateGraph, START, END
# from langgraph.graph.message import add_messages
# from langchain_openai import ChatOpenAI
# from langchain_core.messages import ToolMessage
# import json
#
# # 2.1 Definir o estado / Define the state
# class AgentState(TypedDict):
#     messages: Annotated[list, add_messages]
#     # Adicione campos de domínio aqui / Add domain fields here
#
# # 2.2 Instanciar o LLM com tools vinculadas / Instantiate LLM with bound tools
# llm = ChatOpenAI(model="gpt-4o-mini")
# llm_with_tools = llm.bind_tools(tools)   # tools: lista de @tool ou StructuredTool
#
# # 2.3 Nó do agente: chama o LLM / Agent node: calls the LLM
# async def agent_node(state: AgentState) -> dict:
#     response = await llm_with_tools.ainvoke(state["messages"])
#     return {"messages": [response]}
#
# # 2.4 Nó de execução de tools / Tool execution node
# async def tools_node(state: AgentState) -> dict:
#     last_message = state["messages"][-1]
#     results = []
#     for tool_call in last_message.tool_calls:
#         tool_fn = tool_registry[tool_call["name"]]   # dict com suas funções
#         result = await tool_fn.ainvoke(tool_call["args"])
#         results.append(ToolMessage(content=str(result), tool_call_id=tool_call["id"]))
#     return {"messages": results}
#
# # 2.5 Função de roteamento condicional / Conditional routing function
# def route(state: AgentState) -> str:
#     last_message = state["messages"][-1]
#     if hasattr(last_message, "tool_calls") and last_message.tool_calls:
#         return "tools"   # ir para nó de tools / go to tools node
#     return END           # resposta final / final response
#
# # 2.6 Construir e compilar o grafo / Build and compile the graph
# builder = StateGraph(AgentState)
# builder.add_node("agent", agent_node)
# builder.add_node("tools", tools_node)
#
# builder.add_edge(START, "agent")
# builder.add_conditional_edges("agent", route)
# builder.add_edge("tools", "agent")   # voltar ao agente após executar tool / back to agent after tool
#
# graph = builder.compile()


# -----------------------------------------------------------------------------
# 3. EXECUTANDO O GRAFO / RUNNING THE GRAPH
# -----------------------------------------------------------------------------

# Invocação simples / Simple invocation:
# result = await graph.ainvoke({"messages": [{"role": "user", "content": user_message}]})
# resposta = result["messages"][-1].content
#
# Streaming de tokens e eventos / Token and event streaming:
# async for event in graph.astream_events({"messages": [...]}, version="v2"):
#     if event["event"] == "on_chat_model_stream":
#         token = event["data"]["chunk"].content
#         yield token   # transmitir ao cliente / stream to client


# -----------------------------------------------------------------------------
# 4. MEMÓRIA PERSISTENTE (CHECKPOINTING)
#    PERSISTENT MEMORY (CHECKPOINTING)
# -----------------------------------------------------------------------------

# LangGraph suporta checkpoints para salvar e restaurar estado entre execuções.
# LangGraph supports checkpoints to save and restore state between runs.
#
# from langgraph.checkpoint.memory import MemorySaver       # em memória / in-memory
# from langgraph.checkpoint.postgres import PostgresSaver   # PostgreSQL (produção / production)
# from langgraph.checkpoint.sqlite import SqliteSaver       # SQLite (desenvolvimento / development)
#
# checkpointer = MemorySaver()
# graph = builder.compile(checkpointer=checkpointer)
#
# # thread_id identifica a conversa / thread_id identifies the conversation
# config = {"configurable": {"thread_id": session_id}}
#
# # Primeira mensagem / First message
# await graph.ainvoke({"messages": [{"role": "user", "content": "oi"}]}, config)
#
# # Segunda mensagem — LangGraph restaura o estado anterior automaticamente
# # Second message — LangGraph restores previous state automatically
# await graph.ainvoke({"messages": [{"role": "user", "content": "e meu pedido?"}]}, config)


# -----------------------------------------------------------------------------
# 5. SISTEMA MULTI-AGENTE COM SUPERVISOR
#    MULTI-AGENT SYSTEM WITH SUPERVISOR
# -----------------------------------------------------------------------------

# Padrão: um nó supervisor decide qual sub-agente especialista invocar.
# Pattern: a supervisor node decides which specialist sub-agent to invoke.
#
# supervisor_node → [billing_agent | support_agent | logistics_agent]
#
# Como implementar / How to implement:
#   1. Crie um grafo separado para cada sub-agente / Create a separate graph for each sub-agent
#   2. Crie um nó supervisor que classifica a intenção do usuário
#      Create a supervisor node that classifies user intent
#   3. Use add_conditional_edges com a função do supervisor
#      Use add_conditional_edges with the supervisor function
#   4. Cada sub-agente retorna ao supervisor ao terminar
#      Each sub-agent returns to supervisor when done
#   5. Alternativa: use langgraph.prebuilt.create_react_agent para sub-agentes simples
#      Alternative: use langgraph.prebuilt.create_react_agent for simple sub-agents


# -----------------------------------------------------------------------------
# 6. REACT AGENT PRÉ-CONSTRUÍDO / PRE-BUILT REACT AGENT
# -----------------------------------------------------------------------------

# LangGraph oferece um helper para criar agentes ReAct sem montar o grafo manualmente.
# LangGraph offers a helper to create ReAct agents without building the graph manually.
#
# from langgraph.prebuilt import create_react_agent
#
# agent = create_react_agent(
#     model=llm,
#     tools=tools,                  # lista de @tool / list of @tool
#     state_modifier=system_prompt, # system prompt como string ou Runnable
#     checkpointer=MemorySaver(),   # opcional: habilita memória / optional: enables memory
# )
#
# result = await agent.ainvoke({"messages": [("user", user_message)]}, config)
# Ideal para agentes simples; use o grafo completo para fluxos customizados.
# Ideal for simple agents; use the full graph for custom flows.


# -----------------------------------------------------------------------------
# 7. DICAS E BOAS PRÁTICAS / TIPS AND BEST PRACTICES
# -----------------------------------------------------------------------------

# Depuração / Debugging:
#   - Ative logs com LANGGRAPH_DEBUG=true na env / Enable logs with LANGGRAPH_DEBUG=true
#   - Use graph.get_state(config) para inspecionar estado atual
#     Use graph.get_state(config) to inspect current state
#   - graph.get_state_history(config) retorna todos os checkpoints
#     graph.get_state_history(config) returns all checkpoints

# Interrupções humanas / Human-in-the-loop:
#   - graph = builder.compile(interrupt_before=["tools"])
#   - O grafo pausa antes de executar tools; humano pode aprovar/rejeitar
#   - Graph pauses before executing tools; human can approve/reject

# Paralelismo / Parallelism:
#   - Adicione múltiplas arestas de um nó para outros nós executarem em paralelo
#   - Add multiple edges from one node to other nodes to execute in parallel
#   - builder.add_edge("agent", "tool_a") e builder.add_edge("agent", "tool_b")
#   - LangGraph executa em paralelo e junta os resultados (fan-in) automaticamente
#   - LangGraph executes in parallel and merges results (fan-in) automatically
