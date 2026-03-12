"""
Exceções específicas do framework para falhas de engine e adaptadores.
Framework-specific exceptions for engine and adapter failures.
"""


class BotFrameworkError(Exception):
    """
    Base para todos os erros do framework.
    Base for all framework errors. Catch this to handle any framework issue.
    """


class LLMProviderError(BotFrameworkError):
    """
    Falha na chamada ao LLM (timeout, rate limit, resposta inválida, etc.).
    Raised when the LLM call fails (timeout, rate limit, bad response, etc.).
    """


class ChannelError(BotFrameworkError):
    """
    Falha ao enviar ou parsear mensagem no canal.
    Raised when a channel adapter fails to send or parse a message.
    """


class StorageError(BotFrameworkError):
    """
    Falha em operação de banco de dados ou cache.
    Raised when a database or cache operation fails.
    """


class ConfigurationError(BotFrameworkError):
    """
    Variáveis de ambiente ou config ausentes/inválidas.
    Raised when required env vars or config are missing/invalid.
    """
