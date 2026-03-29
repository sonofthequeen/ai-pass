"""Simple data models."""

from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class Message:
    role: str
    content: str


@dataclass
class Plan:
    tools: list[str] = field(default_factory=list)
    steps: list[str] = field(default_factory=list)

    def add_tool(self, tool_name: str) -> None:
        self.tools.append(tool_name)

    def add_step(self, step: str) -> None:
        self.steps.append(step)


@dataclass
class ToolResult:
    tool_name: str
    output: str
    success: bool = True
