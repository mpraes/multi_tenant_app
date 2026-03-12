"""
CLI para gerenciar a configuração do bot em tempo de execução.
CLI to manage bot configuration at runtime.

Uso / Usage (run from backend/):
    uv run python -m src.cli show
    uv run python -m src.cli set name "Meu Bot"
    uv run python -m src.cli set llm_provider groq
    uv run python -m src.cli set system_prompt "Você é um assistente..."
    uv run python -m src.cli reset

As alterações são salvas em backend/config.json e aplicadas na próxima inicialização.
Changes are saved to backend/config.json and applied on next startup.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

# Localizado em backend/config.json / Located at backend/config.json
CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.json"

# Campos editáveis e seus tipos / Editable fields and their types
FIELDS: dict[str, type] = {
    "name": str,
    "system_prompt": str,
    "llm_provider": str,
    "llm_model": str,
    "llm_temperature": float,
    "llm_max_tokens": int,
    "rag_enabled": bool,
    "history_window": int,
}


def _load() -> dict:
    """Lê config.json ou retorna vazio. / Reads config.json or returns empty dict."""
    if CONFIG_PATH.exists():
        return json.loads(CONFIG_PATH.read_text())
    return {}


def _save(data: dict) -> None:
    """Escreve config.json. / Writes config.json."""
    CONFIG_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False))


def _parse_value(key: str, raw: str) -> Any:
    """
    Converte o valor bruto para o tipo do campo.
    Converts the raw string value to the field's type.
    """
    typ = FIELDS[key]
    if raw.lower() in ("null", "none", ""):
        return None
    if typ is bool:
        return raw.lower() in ("true", "1", "yes", "sim")
    return typ(raw)


# ── Comandos / Commands ────────────────────────────────────────────────────────

def cmd_show(_args: argparse.Namespace) -> None:
    """
    Exibe a configuração atual (defaults + overrides de config.json).
    Shows the current configuration (defaults + config.json overrides).
    """
    from src.config.settings import CONFIG, CONFIG_PATH as _cp, settings

    overrides = _load()
    print("=" * 52)
    print("  BotConfig  (settings.py defaults + config.json)")
    print("=" * 52)
    rows = [
        ("name",            CONFIG.name),
        ("system_prompt",   CONFIG.system_prompt),
        ("llm_provider",    CONFIG.llm_provider or "(herda settings)"),
        ("llm_model",       CONFIG.llm_model or "(herda settings)"),
        ("llm_temperature", CONFIG.llm_temperature),
        ("llm_max_tokens",  CONFIG.llm_max_tokens),
        ("rag_enabled",     CONFIG.rag_enabled),
        ("history_window",  CONFIG.history_window),
    ]
    for k, v in rows:
        marker = " *" if k in overrides else "  "
        print(f"{marker} {k:<20} {v!r}")

    print("\n  * campo sobrescrito por config.json / field overridden by config.json")

    print("\n" + "=" * 52)
    print("  Settings  (variáveis de ambiente / env vars)")
    print("=" * 52)
    env_rows = [
        ("llm_provider",     settings.llm_provider),
        ("openai_model",     settings.openai_model),
        ("groq_model",       settings.groq_model),
        ("anthropic_model",  settings.anthropic_model),
        ("bedrock_model_id", settings.bedrock_model_id),
        ("ollama_model",     settings.ollama_model),
        ("database_url",     settings.database_url),
        ("app_env",          settings.app_env),
        ("rag_enabled",      settings.rag_enabled),
    ]
    for k, v in env_rows:
        print(f"   {k:<20} {v!r}")

    print(f"\n  config.json: {_cp}")


def cmd_set(args: argparse.Namespace) -> None:
    """
    Define um campo em config.json.
    Sets a field in config.json.
    """
    key: str = args.key
    parsed = _parse_value(key, args.value)

    overrides = _load()
    overrides[key] = parsed
    _save(overrides)

    print(f"✓ {key} = {parsed!r}")
    print(f"  Salvo em / Saved to: {CONFIG_PATH}")
    print("  Reinicie o servidor para aplicar. / Restart the server to apply.")


def cmd_reset(_args: argparse.Namespace) -> None:
    """
    Remove config.json, voltando aos defaults de settings.py.
    Deletes config.json, reverting to settings.py defaults.
    """
    if CONFIG_PATH.exists():
        CONFIG_PATH.unlink()
        print(f"✓ config.json removido. / config.json deleted.")
    else:
        print("config.json não existe. Nada a remover. / config.json does not exist.")
    print("  Reinicie o servidor para aplicar. / Restart the server to apply.")


# ── Entry point ────────────────────────────────────────────────────────────────

def main() -> None:
    """Ponto de entrada do CLI. / CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="python -m src.cli",
        description="Gerencia a configuração do bot / Manage bot configuration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    sub = parser.add_subparsers(dest="command", required=True)

    # show
    sub.add_parser("show", help="Exibe a configuração atual / Show current config")

    # set
    p_set = sub.add_parser("set", help="Define um campo / Set a field value")
    p_set.add_argument(
        "key",
        choices=list(FIELDS),
        metavar="KEY",
        help=f"Campo a definir / Field to set. Opções: {', '.join(FIELDS)}",
    )
    p_set.add_argument("value", help="Valor (use 'null' para limpar) / Value (use 'null' to clear)")

    # reset
    sub.add_parser("reset", help="Remove config.json (volta aos defaults) / Remove overrides")

    args = parser.parse_args()
    {"show": cmd_show, "set": cmd_set, "reset": cmd_reset}[args.command](args)


if __name__ == "__main__":
    main()
