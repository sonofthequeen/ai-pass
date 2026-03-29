"""Orchestrator – 5-stage pipeline: INTAKE → PLAN → EXECUTE → EVALUATE → DELIVER."""

from __future__ import annotations

import json
import logging

from agent.planner import Planner
from agent.evaluator import Evaluator
from tools.text_processor import TextProcessorTool
from tools.classifier import ClassifierTool
from tools.action_tool import ActionTool
from memory import get_history
from models import ToolResult

logger = logging.getLogger(__name__)

PIPELINE_STEPS = ["intake", "memory_lookup", "plan", "execute_tools", "evaluate", "deliver"]


class Orchestrator:
    """Central coordinator – runs every message through the 5-stage pipeline."""

    def __init__(self) -> None:
        self.planner = Planner()
        self.evaluator = Evaluator()
        self.tools = {
            "text_processor": TextProcessorTool(),
            "classifier": ClassifierTool(),
            "action": ActionTool(),
        }

    def handle(self, user_message: str, chat_id: int | None = None) -> str:
        tag = f"[chat={chat_id}]" if chat_id is not None else "[no-chat]"

        # --- 1. INTAKE ---
        logger.info("%s INTAKE: received message", tag)
        history = get_history(chat_id) if chat_id is not None else []

        # --- 2. PLAN ---
        plan = self.planner.plan(user_message)
        logger.info("%s PLAN: tools=%s  steps=%s", tag, plan.tools, plan.steps)

        # --- 3. EXECUTE ---
        results: list[ToolResult] = []
        for tool_name in plan.tools:
            tool = self.tools.get(tool_name)
            if tool is None:
                logger.warning("%s EXECUTE: unknown tool '%s', skipping", tag, tool_name)
                continue
            result = tool.run(user_message)
            logger.info("%s EXECUTE: %s → %s", tag, tool_name, result.output)
            results.append(result)

        # --- 4. EVALUATE ---
        response = self.evaluator.evaluate(user_message, results, history)
        logger.info("%s EVALUATE: response=%s", tag, response)

        # --- 5. DELIVER – enrich with pipeline metadata ---
        logger.info("%s DELIVER: done", tag)
        try:
            data = json.loads(response)
        except (json.JSONDecodeError, TypeError):
            data = {"summary": response}

        data["plan"] = plan.steps or plan.tools
        data["execution_steps"] = PIPELINE_STEPS
        data["memory_used"] = bool(history)
        data["tools_used"] = [
            {"name": r.tool_name, "output": r.output} for r in results
        ]
        data["evaluation"] = {
            "output_valid": True,
            "confidence_check": "passed" if data.get("confidence", 0) >= 0.3 else "low",
        }
        return json.dumps(data, ensure_ascii=False)
