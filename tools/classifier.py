"""Intent classifier tool – uses OpenAI to classify user intent."""

from __future__ import annotations

import logging

from config import get_openai_client, MODEL
from models import ToolResult
from tools.base import BaseTool

logger = logging.getLogger(__name__)


class ClassifierTool(BaseTool):
    name = "classifier"

    def run(self, input_text: str) -> ToolResult:
        """Classify the user's intent via GPT."""
        try:
            resp = get_openai_client().chat.completions.create(
                model=MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "Classify the user message into exactly one intent. "
                            "Choose from: question, task, greeting, feedback, other. "
                            "Reply with the single intent word only."
                        ),
                    },
                    {"role": "user", "content": input_text},
                ],
                max_tokens=10,
                temperature=0,
            )
            intent = resp.choices[0].message.content.strip().lower()
            return ToolResult(tool_name=self.name, output=intent, success=True)
        except Exception as exc:
            logger.error("ClassifierTool error: %s", exc)
            return ToolResult(tool_name=self.name, output="other", success=False)
