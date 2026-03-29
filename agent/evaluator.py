"""Evaluator – uses OpenAI to produce a structured final response."""

from __future__ import annotations

import json
import logging
import re

from config import get_openai_client, MODEL
from models import ToolResult

logger = logging.getLogger(__name__)


def _strip_code_fences(text: str) -> str:
    """Remove markdown ```json ... ``` wrappers if present."""
    text = text.strip()
    m = re.match(r"^```(?:json)?\s*\n?(.*?)\n?\s*```$", text, re.DOTALL)
    return m.group(1).strip() if m else text


class Evaluator:
    """Evaluates tool results and returns a structured JSON response."""

    def evaluate(
        self,
        user_message: str,
        results: list[ToolResult],
        history: list[dict] | None = None,
    ) -> str:
        """Synthesise tool outputs into a structured answer via GPT."""
        tool_outputs = "\n".join(
            f"- {r.tool_name}: {r.output}" for r in results
        )

        # Build conversation context from memory
        history_block = ""
        if history:
            lines = []
            for msg in history[-10:]:  # last 10 messages for context
                lines.append(f"{msg['role']}: {msg['content']}")
            history_block = "\n".join(lines)

        try:
            messages = [
                {
                    "role": "system",
                    "content": (
                        "You are an evaluator. Given the user message, conversation history, "
                        "and tool outputs, produce a concise, helpful answer.\n"
                        "Use the conversation history to maintain context across messages.\n"
                        "Reply ONLY with a JSON object:\n"
                        '{"task_type": "...", "summary": "...", "priority": "low|medium|high", '
                        '"suggested_action": "...", "confidence": 0.0}\n'
                        "task_type = the type of user request (e.g. question, task, greeting, feedback, other).\n"
                        "summary = your concise answer to the user.\n"
                        "priority = how urgent the request is.\n"
                        "suggested_action = suggested next step for the user.\n"
                        "confidence = your confidence in the response, a float between 0.0 and 1.0."
                    ),
                },
            ]

            user_content = ""
            if history_block:
                user_content += f"Conversation history:\n{history_block}\n\n"
            user_content += f"Current message: {user_message}\n\n"
            user_content += f"Tool outputs:\n{tool_outputs}"

            messages.append({"role": "user", "content": user_content})

            resp = get_openai_client().chat.completions.create(
                model=MODEL,
                messages=messages,
                max_tokens=300,
                temperature=0.3,
            )
            raw = resp.choices[0].message.content.strip()
            raw = _strip_code_fences(raw)
            # Validate JSON and ensure all required fields
            data = json.loads(raw)
            data.setdefault("task_type", "other")
            data.setdefault("summary", "")
            data.setdefault("priority", "medium")
            data.setdefault("suggested_action", data.pop("action", ""))
            data.setdefault("confidence", 0.5)
            return json.dumps(data, ensure_ascii=False)
        except json.JSONDecodeError:
            logger.warning("Evaluator returned non-JSON, wrapping raw response")
            return json.dumps(
                {"task_type": "other", "summary": raw, "priority": "medium", "suggested_action": "Review response", "confidence": 0.4},
                ensure_ascii=False,
            )
        except Exception as exc:
            logger.error("Evaluator error: %s", exc)
            return json.dumps(
                {
                    "task_type": "other",
                    "summary": "Sorry, I couldn't process your request.",
                    "priority": "medium",
                    "suggested_action": "Please try again.",
                    "confidence": 0.0,
                },
                ensure_ascii=False,
            )
