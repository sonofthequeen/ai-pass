"""Planner – decides which tools to run and in what order (stub)."""

from __future__ import annotations

from models import Plan


class Planner:
    """Creates an execution plan from user input."""

    def plan(self, user_message: str) -> Plan:
        """Return a plan with an ordered list of tools. Replace with LLM logic later."""
        p = Plan()
        # Stub: always run classifier then text_processor
        p.add_tool("classifier")
        p.add_tool("text_processor")
        p.add_step(f"Classify intent for: {user_message[:50]}")
        p.add_step("Process the message text")
        p.add_step("Return result to user")
        return p
