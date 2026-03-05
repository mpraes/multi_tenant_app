"""Framework-specific exceptions for engine and adapter failures."""


class BotFrameworkError(Exception):
    """Base for all framework errors. Catch this to handle any framework issue."""


class TenantNotFoundError(BotFrameworkError):
    """Raised when a tenant slug has no registered config."""
    def __init__(self, slug: str) -> None:
        super().__init__(f"No tenant found for slug '{slug}'. "
                         "Run scripts/new_client.py or register it in customers/.")
        self.slug = slug


class LLMProviderError(BotFrameworkError):
    """Raised when the LLM call fails (timeout, rate limit, bad response, etc.)."""


class ChannelError(BotFrameworkError):
    """Raised when a channel adapter fails to send or parse a message."""


class StorageError(BotFrameworkError):
    """Raised when a database or cache operation fails."""


class ConfigurationError(BotFrameworkError):
    """Raised when required env vars or tenant config are missing/invalid."""
