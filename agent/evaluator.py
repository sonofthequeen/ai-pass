"""Evaluator – judges tool outputs and produces a final answer (stub)."""

from __future__ import annotations

from models import ToolResult


class Evaluator:
    """Evaluates tool results and returns a user-facing response."""

    def evaluate(self, user_message: str, results: list[ToolResult]) -> str:
        """Return a response based on all tool results. Replace with LLM logic later."""
        if all(r.success for r in results):
            return f"[AI-PASS stub] You said: {user_message}"
        return "[AI-PASS stub] Sorry, something went wrong."
