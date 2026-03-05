"""
Tools / Function Calling — biblioteca de tools reutilizáveis entre clientes.

Este pacote centraliza tools que qualquer tenant pode usar com o Agent.
Cada tool é uma função async que recebe parâmetros e retorna uma string
que o LLM usa para formular a resposta final.

Organização sugerida:
    tools/
    ├── __init__.py         ← este arquivo (registro central)
    ├── http_tools.py       ← consultas a APIs externas
    ├── date_tools.py       ← cálculos de data/hora
    ├── search_tools.py     ← busca em bases de conhecimento
    └── crm_tools.py        ← integração com CRM do cliente

Como criar uma nova tool:
  1. Implemente a função async em um dos módulos acima
  2. Crie um Tool(...) com name, description, parameters e fn
  3. Exporte-a aqui ou importe diretamente no flows.py do cliente

Exemplo de uso no flows.py de um cliente:
    from src.core.agent import Agent, Tool
    from src.tools import buscar_pedido_tool, consultar_estoque_tool

    async def handle_pedido(ctx: ConversationContext) -> str:
        agent = Agent(
            provider=get_llm_provider(ctx.tenant_config.llm_provider),
            tools=[buscar_pedido_tool, consultar_estoque_tool],
        )
        return await agent.run(
            system_prompt=ctx.tenant_config.effective_system_prompt(),
            messages=ctx.history_as_openai_messages(),
        )
"""

from __future__ import annotations

# Importe e reexporte as tools que quiser disponibilizar globalmente:
# from src.tools.http_tools import consultar_cep_tool
# from src.tools.date_tools import calcular_prazo_tool

__all__: list[str] = []
