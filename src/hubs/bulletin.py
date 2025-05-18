"""Shared bulletin for storing agent communications."""

from __future__ import annotations

from typing import Any


class Bulletin:
    """A simple in-memory bulletin that records all messages."""

    def __init__(self) -> None:
        self._messages: list[dict[str, Any]] = []

    def post(self, message: dict[str, Any]) -> None:
        """Add a message to the bulletin."""
        self._messages.append(message)

    def history(self) -> list[dict[str, Any]]:
        """Return the entire bulletin history."""
        return list(self._messages)
