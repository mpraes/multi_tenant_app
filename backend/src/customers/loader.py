"""
Tenant registry — auto-discovers and caches TenantConfig instances.

How it works:
  - On first call, scans every subdirectory of customers/ for a config.py
    that exposes a CONFIG = TenantConfig(...) variable.
  - Results are cached in-process (restart to reload).

To register a new client:
  1. Run scripts/new_client.py <slug> "<Name>"   — creates the folder
  2. Edit customers/<slug>/config.py             — fill in the config
  No code changes needed here.
"""

from __future__ import annotations

import importlib
import pkgutil
from functools import lru_cache
from pathlib import Path

from src.customers.base import TenantConfig
from src.utils.logging import get_logger

logger = get_logger(__name__)

# Directory where client packages live
_CUSTOMERS_PKG = "src.customers"
_CUSTOMERS_DIR = Path(__file__).parent


@lru_cache(maxsize=1)
def _load_all_tenants() -> dict[str, TenantConfig]:
    """
    Walk customers/ and import every config.py that has a CONFIG attribute.
    Returns a dict of {slug: TenantConfig}.
    """
    registry: dict[str, TenantConfig] = {}

    for pkg_info in pkgutil.iter_modules([str(_CUSTOMERS_DIR)]):
        if not pkg_info.ispkg:
            continue  # skip non-package files (loader.py, base.py, __init__.py)

        slug = pkg_info.name
        module_path = f"{_CUSTOMERS_PKG}.{slug}.config"

        try:
            module = importlib.import_module(module_path)
        except ModuleNotFoundError:
            logger.debug("customers/%s has no config.py — skipping.", slug)
            continue

        config: TenantConfig | None = getattr(module, "CONFIG", None)

        if not isinstance(config, TenantConfig):
            logger.warning("customers/%s/config.py has no valid CONFIG — skipping.", slug)
            continue

        registry[slug] = config
        logger.info("Registered tenant: %s (%s)", slug, config.name)

    return registry


def get_tenant_config(slug: str) -> TenantConfig | None:
    """
    Return the TenantConfig for a slug, or None if not found.

    Called by TenantMiddleware on every request — result is cached.
    """
    return _load_all_tenants().get(slug)


def list_tenants() -> list[TenantConfig]:
    """Return all registered tenant configs. Useful for admin endpoints."""
    return list(_load_all_tenants().values())


def reload_tenants() -> None:
    """
    Force-reload the tenant registry (e.g. after hot-adding a new client).
    Only needed in long-running processes; a restart also works.
    """
    _load_all_tenants.cache_clear()
    _load_all_tenants()
