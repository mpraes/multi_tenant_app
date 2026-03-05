"""
Retriever — busca semântica no vector store configurado.

Responsável por receber uma query em texto, vetorizá-la e retornar os
chunks de documentos mais relevantes da base de conhecimento do tenant.

Cada tenant tem sua própria coleção/namespace no vector store,
garantindo isolamento total entre bases de conhecimento.
"""

from __future__ import annotations


class Retriever:
    """
    Interface de busca semântica para um tenant específico.

    Instanciar com o slug do tenant garante que a busca é sempre
    restrita à coleção daquele cliente.

    Uso no engine (adicionar como middleware ou chamar no handler):
        retriever = Retriever(tenant_slug="acme")
        chunks = await retriever.search("como cancelar meu pedido", top_k=3)
        ctx.retrieved_context = "\\n\\n".join(chunks)

    TODO: Implementar quando RAG for necessário para algum cliente.
    """

    def __init__(self, tenant_slug: str, top_k: int = 3) -> None:
        """
        Args:
            tenant_slug: Isola a busca na coleção do tenant.
            top_k:       Quantos chunks retornar. Mais chunks = mais contexto,
                         mas ocupa tokens do LLM. Recomendado: 3–5.
        """
        self._tenant_slug = tenant_slug
        self._top_k = top_k
        self._store = None   # inicializado em _get_store()

    async def search(self, query: str) -> list[str]:
        """
        Busca os chunks mais relevantes para a query.

        Returns:
            Lista de strings (chunks de texto) ordenados por relevância.
            Retorna lista vazia se nenhum chunk relevante for encontrado.

        Implementação pendente:
          - Inicializar o vector store (Chroma, pgvector, Pinecone) via _get_store()
          - Vetorizar a query com o mesmo modelo usado na indexação
          - Chamar store.similarity_search(query_vector, k=self._top_k)
          - Filtrar por tenant_slug (metadado) para garantir isolamento
          - Retornar [doc.page_content for doc in results]
        """
        raise NotImplementedError(
            "Retriever.search() não implementado. "
            "Habilite RAG instalando chromadb e implementando este método."
        )

    def _get_store(self):
        """
        Inicializa e retorna o cliente do vector store configurado.

        Lê RAG_VECTOR_STORE do settings para decidir qual provider usar:
            chromadb  → PersistentClient(path=settings.rag_chroma_path)
            pgvector  → SQLAlchemy + pgvector extension
            pinecone  → pinecone.Index(index_name=...)

        Cachear o cliente em self._store para não reconectar a cada busca.
        """
        raise NotImplementedError
