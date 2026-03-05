"""
Indexer — processa e indexa documentos no vector store.

Executado offline (não durante o request) para popular a base de
conhecimento de um tenant. Rode após receber novos documentos do cliente.

Formatos suportados (a implementar conforme necessidade):
    PDF      → extrair texto por página com pypdf ou pdfplumber
    DOCX     → python-docx
    Markdown → parse direto
    URLs     → crawl com httpx + BeautifulSoup
    CSV/XLSX → pandas

Execução (exemplo via script):
    python -c "
    import asyncio
    from src.rag.indexer import Indexer
    asyncio.run(Indexer('acme').index_directory('docs/acme/'))
    "

Estratégia de chunking:
    Documentos longos precisam ser divididos em chunks antes de indexar.
    Chunk ideal: 300–500 tokens com 50 tokens de overlap entre chunks.
    Chunks muito pequenos perdem contexto; muito grandes desperdiçam tokens.
"""

from __future__ import annotations

from pathlib import Path


class Indexer:
    """
    Processa documentos e os indexa no vector store do tenant.

    Um tenant pode ter múltiplos documentos — todos indexados na mesma
    coleção, identificados por metadados (source, page, etc.).

    TODO: Implementar quando o primeiro cliente precisar de RAG.
    """

    def __init__(self, tenant_slug: str) -> None:
        """
        Args:
            tenant_slug: Define a coleção/namespace no vector store.
                         Documentos de tenants diferentes NUNCA se misturam.
        """
        self._tenant_slug = tenant_slug

    async def index_file(self, path: Path) -> int:
        """
        Indexa um único arquivo no vector store.

        Returns:
            Número de chunks indexados.

        Implementação pendente:
          - Detectar tipo do arquivo (sufixo) e chamar o parser correto
          - Dividir texto em chunks (ex: RecursiveCharacterTextSplitter)
          - Vetorizar chunks com o modelo de embeddings configurado
          - Upsert no vector store com metadados: {tenant, source, page}
          - Retornar len(chunks)
        """
        raise NotImplementedError

    async def index_directory(self, directory: str | Path) -> int:
        """
        Indexa todos os arquivos suportados em um diretório recursivamente.

        Returns:
            Total de chunks indexados em todos os arquivos.
        """
        raise NotImplementedError

    async def delete_tenant_index(self) -> None:
        """
        Remove todos os documentos do tenant do vector store.

        Usar antes de reindexar do zero para evitar duplicatas.
        """
        raise NotImplementedError
