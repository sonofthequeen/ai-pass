"""Text processing tool – uses OpenAI to summarise / process text."""

from __future__ import annotations

import logging

from config import get_openai_client, MODEL
from models import ToolResult
from tools.base import BaseTool

logger = logging.getLogger(__name__)


class TextProcessorTool(BaseTool):
    name = "text_processor"

    def run(self, input_text: str) -> ToolResult:
        """Summarise or rephrase the user's message via GPT."""
        try:
            resp = get_openai_client().chat.completions.create(
                model=MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a concise text processor. "
                            "Summarise or clarify the user's message in 1-2 sentences."
                        ),
                    },
                    {"role": "user", "content": input_text},
                ],
                max_tokens=150,
                temperature=0.3,
            )
            summary = resp.choices[0].message.content.strip()
            return ToolResult(tool_name=self.name, output=summary, success=True)
        except Exception as exc:
            logger.error("TextProcessorTool error: %s", exc)
            return ToolResult(
                tool_name=self.name, output=input_text, success=False
            )
