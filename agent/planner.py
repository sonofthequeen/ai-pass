"""Planner – uses OpenAI to decide which tools to run and in what order."""

from __future__ import annotations

import json
import logging

from config import get_openai_client, MODEL
from models import Plan

logger = logging.getLogger(__name__)

AVAILABLE_TOOLS = ["classifier", "text_processor", "action"]


class Planner:
    """Creates an execution plan from user input via GPT."""

    def plan(self, user_message: str) -> Plan:
        """Ask GPT which tools to run and return a Plan."""
        try:
            resp = get_openai_client().chat.completions.create(
                model=MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a planning module. Given a user message, "
                            "decide which tools to run and in what order.\n"
                            f"Available tools: {AVAILABLE_TOOLS}\n"
                            "Reply ONLY with a JSON object: "
                            '{"tools": ["tool1", "tool2"], '
                            '"steps": ["step description 1", "step description 2"]}\n'
                            "Choose only the tools that are relevant. "
                            "Always include \"classifier\" first if the intent is unclear."
                        ),
                    },
                    {"role": "user", "content": user_message},
                ],
                max_tokens=200,
                temperature=0,
            )
            raw = resp.choices[0].message.content.strip()
            data = json.loads(raw)
            p = Plan()
            for t in data.get("tools", []):
                if t in AVAILABLE_TOOLS:
                    p.add_tool(t)
            for s in data.get("steps", []):
                p.add_step(s)
            # Guarantee at least one tool
            if not p.tools:
                p.add_tool("text_processor")
                p.add_step("Fallback: process the message text")
            return p
        except Exception as exc:
            logger.error("Planner error: %s", exc)
            # Safe fallback plan
            p = Plan()
            p.add_tool("classifier")
            p.add_tool("text_processor")
            p.add_step("Fallback: classify then process")
            return p
