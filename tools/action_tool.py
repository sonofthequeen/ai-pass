"""Action execution tool – uses OpenAI to suggest a concrete action."""

from __future__ import annotations

import logging

from config import get_openai_client, MODEL
from models import ToolResult
from tools.base import BaseTool

logger = logging.getLogger(__name__)


class ActionTool(BaseTool):
    name = "action"

    def run(self, input_text: str) -> ToolResult:
        """Suggest the next best action for the user via GPT."""
        try:
            resp = get_openai_client().chat.completions.create(
                model=MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Based on the user's message, suggest one short, "
                            "actionable next step they should take. "
                            "Reply in one sentence."
                        ),
                    },
                    {"role": "user", "content": input_text},
                ],
                max_tokens=100,
                temperature=0.4,
            )
            action = resp.choices[0].message.content.strip()
            return ToolResult(tool_name=self.name, output=action, success=True)
        except Exception as exc:
            logger.error("ActionTool error: %s", exc)
            return ToolResult(
                tool_name=self.name, output="No action suggested.", success=False
            )
