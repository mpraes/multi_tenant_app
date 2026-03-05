"""
Endpoints de administração — gerenciamento de tenants em runtime.

Proteja estas rotas com autenticação antes de expor em produção.
Sugestão: API Key no header X-Admin-Key verificada por um middleware.

Uso típico durante uma consultoria:
  - Listar tenants carregados sem precisar acessar o servidor
  - Forçar reload após editar um config.py sem reiniciar o processo
  - Verificar configurações de um tenant específico
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

router = APIRouter(prefix="/admin", tags=["admin"])


def _require_admin_key():
    """
    Dependency que verifica a API key administrativa.

    Implementação pendente:
      - Ler X-Admin-Key do header (via Header(...))
      - Comparar com settings.admin_api_key (adicionar ao Settings)
      - Se inválida: raise HTTPException(403)
      - Se válida: retornar True

    TODO: implementar antes de expor em produção.
    """
    pass  # substituir por verificação real


@router.get("/tenants")
async def list_tenants(_=Depends(_require_admin_key)) -> list[dict]:
    """
    Lista todos os tenants registrados com suas configurações principais.

    Útil para verificar se um novo cliente foi detectado após deploy.
    """
    from src.customers.loader import list_tenants as _list
    return [
        {
            "slug": t.slug,
            "name": t.name,
            "channels": t.enabled_channels,
            "llm_provider": t.llm_provider,
            "llm_model": t.llm_model,
            "rag_enabled": t.rag_enabled,
        }
        for t in _list()
    ]


@router.post("/tenants/reload")
async def reload_tenants(_=Depends(_require_admin_key)) -> dict:
    """
    Força o reload do registry de tenants sem reiniciar o servidor.

    Use após adicionar ou editar um customers/<slug>/config.py em produção
    sem querer fazer um downtime completo.
    """
    from src.customers.loader import reload_tenants as _reload
    _reload()
    from src.customers.loader import list_tenants as _list
    tenants = _list()
    return {"reloaded": len(tenants), "slugs": [t.slug for t in tenants]}


@router.get("/tenants/{slug}")
async def get_tenant(slug: str, _=Depends(_require_admin_key)) -> dict:
    """
    Retorna a configuração completa de um tenant específico.

    Útil para depurar: verificar se o prompt e os canais estão corretos.
    """
    from src.customers.loader import get_tenant_config
    config = get_tenant_config(slug)
    if not config:
        raise HTTPException(status_code=404, detail=f"Tenant '{slug}' não encontrado.")
    return {
        "slug": config.slug,
        "name": config.name,
        "channels": config.enabled_channels,
        "llm_provider": config.llm_provider,
        "llm_model": config.llm_model,
        "rag_enabled": config.rag_enabled,
        "history_window": config.history_window,
        "has_system_prompt_override": config.system_prompt_override is not None,
        "flows": list(config.flows.keys()),
        "extra": config.extra,
    }
