"""Base class for all tools."""

from __future__ import annotations

from abc import ABC, abstractmethod
from models import ToolResult


class BaseTool(ABC):
    """Every tool must implement `run`."""

    name: str = "base"

    @abstractmethod
    def run(self, input_text: str) -> ToolResult:
        """Execute the tool and return a ToolResult."""
        ...
