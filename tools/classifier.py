"""Intent classifier tool (stub)."""

from __future__ import annotations

from models import ToolResult
from tools.base import BaseTool


class ClassifierTool(BaseTool):
    name = "classifier"

    def run(self, input_text: str) -> ToolResult:
        """Stub: always returns 'general' intent."""
        return ToolResult(
            tool_name=self.name,
            output="general",
            success=True,
        )
