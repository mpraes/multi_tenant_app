"""
API — endpoints HTTP além dos canais de chat.

Este pacote expõe rotas administrativas e operacionais que não fazem
parte do fluxo de mensagens, mas são necessárias para operar o sistema:

    api/admin.py    → gerenciamento de tenants, reload de config
    api/webhooks.py → endpoints de callback para integrações externas
    api/health.py   → health/readiness checks detalhados

Montagem em main.py:
    from src.api import router as api_router
    app.include_router(api_router, prefix="/api/v1")

Autenticação:
    Proteja todos os endpoints deste pacote com API key ou JWT.
    Nunca exponha endpoints admin sem autenticação em produção.
"""
