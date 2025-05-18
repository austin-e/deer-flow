"""Simple orchestrator for assigning tasks to agents."""

from __future__ import annotations

from typing import Any


class Orchestrator:
    """Assign tasks to agents and keeps track of the assignments."""

    def __init__(self) -> None:
        self.task_queue: list[dict[str, Any]] = []

    def assign(self, agent_name: str, task: str) -> dict[str, Any]:
        """Assign a task to an agent."""
        assignment = {"agent": agent_name, "task": task}
        self.task_queue.append(assignment)
        return assignment
