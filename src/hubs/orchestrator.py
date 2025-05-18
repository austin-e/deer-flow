"""Simple orchestrator for assigning tasks to agents."""

from __future__ import annotations

from typing import Any

from src.config.agents import AGENT_LLM_MAP


class Orchestrator:
    """Assign tasks to agents and keeps track of the assignments."""

    def __init__(self) -> None:
        self.task_queue: list[dict[str, Any]] = []

    def assign(
        self, agent_name: str, task: str, llm_type: str | None = None
    ) -> dict[str, Any]:
        """Assign a task to an agent.

        Parameters
        ----------
        agent_name : str
            Name of the agent the task is assigned to.
        task : str
            The task description.
        llm_type : str | None, optional
            The LLM type powering this agent. If ``None`` it is looked up
            in :data:`AGENT_LLM_MAP` and defaults to ``"basic"`` when the
            agent name is not present.
        """

        resolved_llm_type = llm_type or AGENT_LLM_MAP.get(agent_name, "basic")
        assignment = {"agent": agent_name, "task": task, "llm_type": resolved_llm_type}
        self.task_queue.append(assignment)
        return assignment
