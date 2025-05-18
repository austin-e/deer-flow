"""Secretary hub responsible for processing reports."""

from __future__ import annotations

from typing import Any

from .bulletin import Bulletin


class Secretary:
    """Processes agent reports and publishes them to the bulletin.

    The secretary itself keeps no internal state other than a reference to the
    shared :class:`Bulletin`, making it safe to scale horizontally.
    """

    def __init__(self, bulletin: Bulletin) -> None:
        self.bulletin = bulletin

    def handle_report(self, agent_name: str, report: str) -> dict[str, Any]:
        """Process a report from an agent and add it to the bulletin."""
        entry = {"agent": agent_name, "report": report}
        self.bulletin.post(entry)
        return entry
