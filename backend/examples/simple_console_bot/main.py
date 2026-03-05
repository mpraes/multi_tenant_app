"""
Console Bot — exemplo mínimo para testar o framework localmente.

Executa o bot no terminal sem precisar de servidor HTTP, Docker ou webhooks.
Ideal para validar o prompt e os flows de um novo cliente antes de subir.

Uso:
    cd backend
    OPENAI_API_KEY=sk-... python examples/simple_console_bot/main.py acme

O tenant precisa estar registrado em customers/<slug>/config.py.
"""

from __future__ import annotations

import asyncio
import sys


async def main(tenant_slug: str) -> None:
    """Loop de conversa no terminal para um tenant específico."""
    # Importações aqui para não quebrar se o pacote não estiver instalado
    from src.core.message import Message, MessageChannel
    from src.core.orchestrator import Orchestrator
    from src.customers.loader import get_tenant_config
    from src.utils.ids import new_session_id
    from src.utils.logging import setup_logging

    setup_logging()

    # Verifica se o tenant existe antes de começar
    config = get_tenant_config(tenant_slug)
    if config is None:
        print(f"❌ Tenant '{tenant_slug}' não encontrado.")
        print("   Verifique se existe customers/{tenant_slug}/config.py com CONFIG = TenantConfig(...)")
        sys.exit(1)

    session_id = new_session_id()
    orchestrator = Orchestrator()

    print(f"\n🤖 Bot: {config.name}")
    print(f"   Modelo: {config.llm_model or 'padrão'} | Canal: console")
    print(f"   Session: {session_id}")
    print("   Digite 'sair' para encerrar.\n")

    while True:
        try:
            user_input = input("Você: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nEncerrando...")
            break

        if user_input.lower() in ("sair", "exit", "quit"):
            break

        if not user_input:
            continue

        message = Message(
            tenant_slug=tenant_slug,
            session_id=session_id,
            user_id="console_user",
            text=user_input,
            channel=MessageChannel.CONSOLE,
        )

        try:
            response = await orchestrator.process(message)
            print(f"\nBot: {response.text}\n")
        except Exception as exc:
            print(f"\n[Erro] {type(exc).__name__}: {exc}\n")


if __name__ == "__main__":
    slug = sys.argv[1] if len(sys.argv) > 1 else "acme"
    asyncio.run(main(slug))
