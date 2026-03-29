"""Text processing tool (stub)."""

from __future__ import annotations

from models import ToolResult
from tools.base import BaseTool


class TextProcessorTool(BaseTool):
    name = "text_processor"

    def run(self, input_text: str) -> ToolResult:
        """Stub: echoes the input back."""
        return ToolResult(
            tool_name=self.name,
            output=f"Processed: {input_text}",
            success=True,
        )
