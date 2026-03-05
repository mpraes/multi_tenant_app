"""Abstract base channel — all adapters must implement this contract."""

from __future__ import annotations

from abc import ABC, abstractmethod

from src.core.message import Message, MessageChannel, Response


class BaseChannel(ABC):
    """
    Contract for every channel adapter (Web, WhatsApp, Telegram, Slack, etc.).

    Lifecycle:
      1. Channel receives a native event (HTTP webhook, WebSocket frame, etc.)
      2. parse_incoming() normalises it into a Message
      3. Engine processes the Message and returns a Response
      4. format_outgoing() converts Response back to channel-native payload
      5. send() delivers it

    To add a new channel:
      1. Create src/channels/<name>.py
      2. Subclass BaseChannel and implement all abstract methods
      3. Mount its router in src/main.py
    """

    @property
    @abstractmethod
    def channel_id(self) -> MessageChannel:
        """Return the MessageChannel enum member for this adapter."""

    @abstractmethod
    async def parse_incoming(self, raw: dict) -> Message:
        """
        Convert the raw channel payload to a canonical Message.

        Args:
            raw: The parsed JSON body from the webhook/event.
        """

    @abstractmethod
    async def format_outgoing(self, response: Response) -> dict:
        """
        Convert an engine Response to the channel-native payload dict.
        The result is sent to the channel API or returned in the HTTP response.
        """

    @abstractmethod
    async def send(self, payload: dict) -> None:
        """
        Deliver the formatted payload to the channel.
        For webhook-reply channels (web_chat, Telegram), this may be a no-op
        and the payload is returned directly in the HTTP response instead.
        """
