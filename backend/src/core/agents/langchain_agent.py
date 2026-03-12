# =============================================================================
# AGENTE COM LANGCHAIN
# AGENT WITH LANGCHAIN
# =============================================================================
#
# O que é LangChain / What is LangChain:
#   LangChain é uma biblioteca de composição de cadeias (chains) e agentes
#   sobre LLMs. Fornece abstrações para prompts, memória, tools, retrievers
#   e runnables compostos via LCEL (LangChain Expression Language).
#
#   LangChain is a library for composing chains and agents over LLMs. It
#   provides abstractions for prompts, memory, tools, retrievers, and
#   runnables composed via LCEL (LangChain Expression Language).
#
# Quando usar / When to use:
#   - Pipelines lineares: RAG, summarization, extraction / Linear pipelines: RAG, etc.
#   - Quando precisar de integrações prontas (>200 integrações) / When needing ready integrations
#   - Prototipagem rápida com chains declarativas / Rapid prototyping with declarative chains
#   - Agentes simples sem controle de fluxo complexo / Simple agents without complex flow control
#   - Para fluxos complexos com estados, prefira LangGraph / For complex stateful flows, prefer LangGraph
#
# Dependências necessárias / Required dependencies:
#   uv add langchain langchain-openai   → com OpenAI / with OpenAI
#   uv add langchain langchain-anthropic → com Anthropic / with Anthropic
#   uv add langchain-community           → integrações extras / extra integrations
#
# =============================================================================


# -----------------------------------------------------------------------------
# 1. CONCEITOS FUNDAMENTAIS / FUNDAMENTAL CONCEPTS
# -----------------------------------------------------------------------------

# Runnable / LCEL (LangChain Expression Language):
#   Qualquer componente LangChain é um Runnable com .invoke(), .ainvoke(),
#   .stream(), .astream(). Compostos com o operador | (pipe).
#
#   Any LangChain component is a Runnable with .invoke(), .ainvoke(),
#   .stream(), .astream(). Composed with the | (pipe) operator.
#
#   chain = prompt | llm | output_parser
#   result = await chain.ainvoke({"input": "oi"})

# Tool (@tool decorator):
#   Função Python anotada que o LLM pode chamar. A docstring vira description.
#   Annotated Python function that LLM can call. Docstring becomes description.
#
#   @tool
#   async def buscar_pedido(numero_pedido: str) -> str:
#       """Busca o status de um pedido pelo número. / Fetches order status by number."""
#       return await db.get_order(numero_pedido)

# Memory (Memória):
#   LangChain oferece diferentes tipos de memória que se integram ao chain.
#   LangChain offers different memory types that integrate into the chain.
#   Para produção, prefira armazenar histórico no banco e passar explicitamente.
#   For production, prefer storing history in DB and passing explicitly.


# -----------------------------------------------------------------------------
# 2. CHAIN BÁSICA COM LCEL / BASIC CHAIN WITH LCEL
# -----------------------------------------------------------------------------

# from langchain_openai import ChatOpenAI
# from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
# from langchain_core.output_parsers import StrOutputParser
# from langchain_core.messages import HumanMessage, AIMessage
#
# # 2.1 Definir o prompt / Define the prompt
# prompt = ChatPromptTemplate.from_messages([
#     ("system", "Você é um assistente de suporte. / You are a support assistant."),
#     MessagesPlaceholder(variable_name="history"),  # histórico injetado / injected history
#     ("human", "{input}"),
# ])
#
# # 2.2 Instanciar o LLM / Instantiate the LLM
# llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
#
# # 2.3 Compor a chain com LCEL / Compose chain with LCEL
# chain = prompt | llm | StrOutputParser()
#
# # 2.4 Invocar / Invoke
# response = await chain.ainvoke({
#     "input": "Qual o status do pedido PED-123?",
#     "history": [
#         HumanMessage(content="oi"),
#         AIMessage(content="Olá! Como posso ajudar?"),
#     ],
# })


# -----------------------------------------------------------------------------
# 3. AGENTE COM TOOLS / AGENT WITH TOOLS
# -----------------------------------------------------------------------------

# from langchain.agents import create_tool_calling_agent, AgentExecutor
# from langchain_core.tools import tool
# from langchain_openai import ChatOpenAI
# from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
#
# # 3.1 Definir tools com o decorator / Define tools with decorator
# @tool
# async def buscar_pedido(numero_pedido: str) -> str:
#     """
#     Busca o status de um pedido pelo número.
#     Fetches order status by number.
#     """
#     # Lógica de busca aqui / Lookup logic here
#     return f"Pedido {numero_pedido}: Em trânsito / In transit"
#
# @tool
# async def cancelar_pedido(numero_pedido: str, motivo: str) -> str:
#     """
#     Cancela um pedido pelo número com o motivo fornecido.
#     Cancels an order by number with the provided reason.
#     """
#     return f"Pedido {numero_pedido} cancelado: {motivo}"
#
# tools = [buscar_pedido, cancelar_pedido]
#
# # 3.2 Prompt — DEVE incluir agent_scratchpad para o loop funcionar
# #     Prompt — MUST include agent_scratchpad for the loop to work
# prompt = ChatPromptTemplate.from_messages([
#     ("system", "Você é um agente de suporte com acesso a ferramentas."),
#     MessagesPlaceholder("chat_history", optional=True),
#     ("human", "{input}"),
#     MessagesPlaceholder("agent_scratchpad"),  # pensamento interno do agente / agent's internal thought
# ])
#
# # 3.3 Criar o agente e o executor / Create agent and executor
# llm = ChatOpenAI(model="gpt-4o-mini")
# agent = create_tool_calling_agent(llm, tools, prompt)
# executor = AgentExecutor(agent=agent, tools=tools, verbose=True, max_iterations=5)
#
# # 3.4 Executar / Execute
# result = await executor.ainvoke({
#     "input": "Qual o status do pedido PED-456?",
#     "chat_history": [],
# })
# response = result["output"]


# -----------------------------------------------------------------------------
# 4. RAG CHAIN (RETRIEVAL AUGMENTED GENERATION)
#    RAG CHAIN (RETRIEVAL AUGMENTED GENERATION)
# -----------------------------------------------------------------------------

# from langchain_openai import ChatOpenAI, OpenAIEmbeddings
# from langchain_community.vectorstores import Chroma  # ou FAISS, Pinecone, etc.
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_core.runnables import RunnablePassthrough
# from langchain_core.output_parsers import StrOutputParser
#
# # 4.1 Criar o retriever (busca semântica) / Create retriever (semantic search)
# embeddings = OpenAIEmbeddings()
# vectorstore = Chroma(persist_directory="./chroma_db", embedding_function=embeddings)
# retriever = vectorstore.as_retriever(search_kwargs={"k": 4})  # top 4 chunks
#
# # 4.2 Prompt RAG / RAG prompt
# rag_prompt = ChatPromptTemplate.from_messages([
#     ("system", """Responda com base APENAS no contexto abaixo.
#                  Answer based ONLY on the context below.
#                  Contexto / Context: {context}"""),
#     ("human", "{question}"),
# ])
#
# # 4.3 Chain RAG com LCEL / RAG chain with LCEL
# def format_docs(docs):
#     return "\n\n".join(doc.page_content for doc in docs)
#
# rag_chain = (
#     {"context": retriever | format_docs, "question": RunnablePassthrough()}
#     | rag_prompt
#     | ChatOpenAI(model="gpt-4o-mini")
#     | StrOutputParser()
# )
#
# answer = await rag_chain.ainvoke("O que é a política de devolução?")

# 4.4 Indexando documentos / Indexing documents:
# from langchain_community.document_loaders import PyPDFLoader, WebBaseLoader
# from langchain.text_splitter import RecursiveCharacterTextSplitter
#
# loader = PyPDFLoader("manual.pdf")         # ou WebBaseLoader("https://...")
# docs = loader.load()
# splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
# chunks = splitter.split_documents(docs)
# vectorstore = Chroma.from_documents(chunks, embeddings, persist_directory="./chroma_db")


# -----------------------------------------------------------------------------
# 5. EXTRACTION / STRUCTURED OUTPUT
#    EXTRAÇÃO / SAÍDA ESTRUTURADA
# -----------------------------------------------------------------------------

# LangChain integra com Pydantic para extrair dados estruturados do LLM.
# LangChain integrates with Pydantic to extract structured data from LLM.
#
# from pydantic import BaseModel, Field
# from langchain_openai import ChatOpenAI
#
# class InfoPedido(BaseModel):
#     numero_pedido: str = Field(description="Número do pedido no formato PED-XXXXX")
#     acao: str = Field(description="Ação solicitada: status | cancelar | alterar_endereco")
#
# llm = ChatOpenAI(model="gpt-4o-mini")
# structured_llm = llm.with_structured_output(InfoPedido)
#
# info = await structured_llm.ainvoke("quero cancelar o pedido PED-789")
# # info.numero_pedido == "PED-789"
# # info.acao == "cancelar"


# -----------------------------------------------------------------------------
# 6. DICAS E BOAS PRÁTICAS / TIPS AND BEST PRACTICES
# -----------------------------------------------------------------------------

# Callbacks e observabilidade / Callbacks and observability:
#   - Integre LangSmith para tracing completo: LANGCHAIN_TRACING_V2=true
#   - Integrate LangSmith for full tracing: LANGCHAIN_TRACING_V2=true
#   - Use CallbackHandler para logs customizados / Use CallbackHandler for custom logs
#   - chain.ainvoke(input, config={"callbacks": [my_handler]})

# Streaming / Streaming:
#   async for chunk in chain.astream({"input": "oi"}):
#       yield chunk   # envia token por token ao cliente / sends token by token to client

# Fallbacks / Fallbacks:
#   llm_com_fallback = ChatOpenAI(model="gpt-4o").with_fallbacks([
#       ChatOpenAI(model="gpt-4o-mini")
#   ])
#   Tenta o modelo principal; se falhar, usa o fallback / Tries main model; falls back if it fails

# LangChain vs LangGraph / LangChain vs LangGraph:
#   - LangChain: chains lineares, RAG, extração / linear chains, RAG, extraction
#   - LangGraph: agentes com estado, fluxo condicional, multi-agente
#                stateful agents, conditional flow, multi-agent
#   - Ambos se complementam; use LangGraph para orquestrar agents LangChain
#   - Both complement each other; use LangGraph to orchestrate LangChain agents
