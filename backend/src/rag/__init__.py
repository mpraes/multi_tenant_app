"""
RAG — Retrieval-Augmented Generation.

Usado quando o cliente tem uma base de conhecimento própria (PDFs, FAQs,
documentação, manuais) que o LLM precisa consultar para responder.

Ative por tenant em customers/<slug>/config.py:
    rag_enabled=True

Fluxo de integração com o engine:
  1. Middleware de RAG detecta rag_enabled=True no tenant_config
  2. Chama Retriever.search(query) com o texto da mensagem
  3. Os chunks recuperados são injetados em ctx.retrieved_context
  4. domain/handlers.py já usa ctx.retrieved_context no system_prompt

Componentes:
    rag/retriever.py  → busca semântica no vector store
    rag/indexer.py    → indexação de documentos (rodar offline/batch)

Providers de vector store suportados (configurar via RAG_VECTOR_STORE no .env):
    chromadb   → local, zero infraestrutura, ótimo para começar
    pgvector   → PostgreSQL com extensão pgvector, boa para produção
    pinecone   → managed, cloud, boa para grandes volumes

Dependências (instalar quando habilitar RAG):
    pip install chromadb sentence-transformers
"""
