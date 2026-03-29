"""Orchestrator – 5-stage pipeline: INTAKE → PLAN → EXECUTE → EVALUATE → DELIVER."""

from __future__ import annotations

import logging

from agent.planner import Planner
from agent.evaluator import Evaluator
from tools.text_processor import TextProcessorTool
from tools.classifier import ClassifierTool
from tools.action_tool import ActionTool
from models import ToolResult

logger = logging.getLogger(__name__)


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

    def handle(self, user_message: str) -> str:
        # --- 1. INTAKE ---
        logger.info("INTAKE: received message")

        # --- 2. PLAN ---
        plan = self.planner.plan(user_message)
        logger.info("PLAN: tools=%s  steps=%s", plan.tools, plan.steps)

        # --- 3. EXECUTE ---
        results: list[ToolResult] = []
        for tool_name in plan.tools:
            tool = self.tools.get(tool_name)
            if tool is None:
                logger.warning("EXECUTE: unknown tool '%s', skipping", tool_name)
                continue
            result = tool.run(user_message)
            logger.info("EXECUTE: %s → %s", tool_name, result.output)
            results.append(result)

        # --- 4. EVALUATE ---
        response = self.evaluator.evaluate(user_message, results)
        logger.info("EVALUATE: response=%s", response)

        # --- 5. DELIVER ---
        logger.info("DELIVER: done")
        return response
