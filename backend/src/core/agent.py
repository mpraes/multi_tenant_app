"""
Agent — execução de multi-step reasoning com tool calls (function calling).

Use este módulo quando o bot precisar ir além de uma única chamada ao LLM:
consultar APIs externas, buscar dados em banco, fazer cálculos, etc.

Fluxo básico (ReAct loop):
  1. LLM recebe mensagem + lista de tools disponíveis
  2. LLM decide chamar uma tool (ex: buscar_pedido)
  3. Agent executa a tool e devolve o resultado ao LLM
  4. LLM decide: chamar outra tool OU gerar resposta final
  5. Resposta final é retornada ao handler

Referência: padrão ReAct (Reason + Act), compatível com OpenAI function calling.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Coroutine


# ── Tool definition ───────────────────────────────────────────────────────────

@dataclass
class Tool:
    """
    Representa uma função que o LLM pode chamar durante o raciocínio.

    Attributes:
        name:        Identificador único (snake_case). Usado pelo LLM para chamar.
        description: Descrição em linguagem natural — o LLM lê isso para decidir
                     quando chamar a tool. Seja específico e conciso.
        parameters:  JSON Schema dos parâmetros. Segue o formato OpenAI function calling.
        fn:          Função async que executa a lógica real.

    Exemplo:
        Tool(
            name="buscar_pedido",
            description="Busca o status de um pedido pelo número.",
            parameters={
                "type": "object",
                "properties": {
                    "numero_pedido": {"type": "string", "description": "Ex: PED-12345"}
                },
                "required": ["numero_pedido"],
            },
            fn=buscar_pedido,
        )
    """
    name: str
    description: str
    parameters: dict[str, Any]
    fn: Callable[..., Coroutine[Any, Any, str]]

    def to_openai_schema(self) -> dict:
        """Converte para o formato de function calling da OpenAI."""
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters,
            },
        }


# ── Agent ─────────────────────────────────────────────────────────────────────

class Agent:
    """
    Executa um loop de raciocínio (ReAct) com chamadas a tools.

    Uso básico em um handler:
        agent = Agent(
            provider=get_llm_provider(),
            tools=[tool_buscar_pedido, tool_consultar_estoque],
            max_steps=5,
        )
        resposta = await agent.run(system_prompt, messages)

    Como adicionar tools para um cliente:
        1. Implemente a função async (ex: async def buscar_pedido(numero_pedido: str) -> str)
        2. Crie um Tool(...) com name, description, parameters e fn
        3. Passe a lista de tools para o Agent no handler do cliente
        4. O LLM decide automaticamente quando e como usar cada tool

    Limite de iterações:
        max_steps evita loops infinitos. Se atingido, retorna o último
        texto parcial disponível ou uma mensagem de erro amigável.
    """

    def __init__(
        self,
        provider: Any,           # BaseLLMProvider
        tools: list[Tool],
        max_steps: int = 5,
    ) -> None:
        """
        Args:
            provider:  Instância de BaseLLMProvider (openai, azure, ollama).
            tools:     Lista de Tools disponíveis para o LLM chamar.
            max_steps: Número máximo de iterações do loop ReAct.
        """
        self._provider = provider
        self._tools = {t.name: t for t in tools}
        self._max_steps = max_steps

    async def run(
        self,
        system_prompt: str,
        messages: list[dict[str, str]],
    ) -> str:
        """
        Executa o loop ReAct e retorna a resposta final em texto.

        Implementação pendente:
          - Chamar provider com tools=self._tools.values() + force_tool_choice
          - Verificar se LLM retornou tool_call ou texto final
          - Se tool_call: executar self._tools[name].fn(**args) e continuar loop
          - Se texto: retornar
          - Se max_steps atingido: retornar mensagem de fallback

        TODO: Implementar quando o cliente precisar de tool calling.
        """
        raise NotImplementedError(
            "Agent.run() ainda não implementado. "
            "Veja docstring para o roteiro de implementação."
        )

    async def _execute_tool(self, name: str, arguments: dict) -> str:
        """
        Executa uma tool pelo nome e retorna o resultado como string.

        O resultado é devolvido ao LLM como uma mensagem de role='tool'.
        Se a tool não existir ou lançar exceção, retorna mensagem de erro
        para que o LLM possa comunicar ao usuário de forma amigável.
        """
        tool = self._tools.get(name)
        if not tool:
            return f"[Erro: tool '{name}' não encontrada]"
        try:
            return await tool.fn(**arguments)
        except Exception as exc:
            return f"[Erro ao executar '{name}': {exc}]"
