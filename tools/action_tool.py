"""Action execution tool (stub)."""

from __future__ import annotations

from models import ToolResult
from tools.base import BaseTool


class ActionTool(BaseTool):
    name = "action"

    def run(self, input_text: str) -> ToolResult:
        """Stub: confirms the action was executed."""
        return ToolResult(
            tool_name=self.name,
            output=f"Action executed for: {input_text}",
            success=True,
        )
