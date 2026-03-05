"""
LLM provider factory.

Usage (inside the engine or tests):
    provider = get_llm_provider()                    # uses global settings
    provider = get_llm_provider("ollama")            # force specific provider
    provider = get_llm_provider(tenant_override="azure_openai")  # tenant override

To add a new provider:
  1. Create src/llm/<name>_provider.py with a class that extends BaseLLMProvider
  2. Add an entry to the _REGISTRY dict below
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.config.settings import settings
from src.core.errors import ConfigurationError

if TYPE_CHECKING:
    from src.llm.base import BaseLLMProvider

# Maps provider slug → (module_path, class_name)
_REGISTRY: dict[str, tuple[str, str]] = {
    "openai": ("src.llm.openai_provider", "OpenAIProvider"),
    "azure_openai": ("src.llm.azure_openai", "AzureOpenAIProvider"),
    "ollama": ("src.llm.local_ollama", "OllamaProvider"),
}


def get_llm_provider(provider_slug: str | None = None) -> "BaseLLMProvider":
    """
    Instantiate and return the configured LLM provider.

    Args:
        provider_slug: Override the global settings.llm_provider value.
                       Useful for per-tenant provider selection.
    """
    slug = provider_slug or settings.llm_provider

    if slug not in _REGISTRY:
        raise ConfigurationError(
            f"Unknown LLM provider '{slug}'. Valid options: {list(_REGISTRY)}"
        )

    module_path, class_name = _REGISTRY[slug]
    import importlib
    module = importlib.import_module(module_path)
    cls = getattr(module, class_name)

    if slug == "openai":
        if not settings.openai_api_key:
            raise ConfigurationError("OPENAI_API_KEY is not set.")
        return cls(api_key=settings.openai_api_key, model=settings.openai_model)

    if slug == "azure_openai":
        if not settings.azure_openai_api_key:
            raise ConfigurationError("AZURE_OPENAI_API_KEY is not set.")
        return cls(
            api_key=settings.azure_openai_api_key,
            endpoint=settings.azure_openai_endpoint,
            deployment=settings.azure_openai_deployment,
            api_version=settings.azure_openai_api_version,
        )

    if slug == "ollama":
        return cls(base_url=settings.ollama_base_url, model=settings.ollama_model)

    raise ConfigurationError(f"Provider '{slug}' is registered but has no factory branch.")
