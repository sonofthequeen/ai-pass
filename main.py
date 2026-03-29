"""AI-PASS – Telegram bot entry point."""

import json
import logging
import sys

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

from config import TELEGRAM_BOT_TOKEN, OPENAI_API_KEY
from memory import add_message, get_history, get_stats, get_recent_interactions
from agent.orchestrator import Orchestrator

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

orchestrator = Orchestrator()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command."""
    await update.message.reply_text("Hello! I'm AI-PASS, your personal assistant. Send me a message!")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle any text message."""
    chat_id = update.effective_chat.id
    user_text = update.message.text
    logger.info("[chat=%s] Incoming message", chat_id)

    # Get structured response from orchestrator (with chat context)
    # NOTE: store user message AFTER getting history so the current message
    # isn't duplicated (orchestrator already passes it as user_message).
    raw_response = orchestrator.handle(user_text, chat_id)

    # Store user message
    add_message(chat_id, "user", user_text)

    # Format for Telegram
    try:
        data = json.loads(raw_response)

        # Core answer
        lines = [
            f"🏷 Type: {data.get('task_type', 'other')}",
            f"📋 {data.get('summary', '')}",
            f"⚡ Priority: {data.get('priority', 'medium')}",
            f"➡️ Action: {data.get('suggested_action', '')}",
            f"🎯 Confidence: {data.get('confidence', 0.5)}",
        ]

        # Pipeline details
        lines.append("")
        lines.append("🔧 Agent Flow:")
        lines.append(f"  Plan: {', '.join(data.get('plan', []))}")
        lines.append(f"  Steps: {' → '.join(data.get('execution_steps', []))}")
        lines.append(f"  Memory used: {'yes' if data.get('memory_used') else 'no'}")

        tools_used = data.get("tools_used", [])
        if tools_used:
            lines.append("  Tools:")
            for t in tools_used:
                lines.append(f"    • {t['name']}: {t['output'][:80]}")

        ev = data.get("evaluation", {})
        lines.append(f"  Eval: valid={ev.get('output_valid')}, confidence={ev.get('confidence_check')}")

        reply = "\n".join(lines)
        # Store the clean summary in memory (not the emoji-formatted text)
        add_message(chat_id, "assistant", data.get("summary", raw_response))
    except (json.JSONDecodeError, TypeError):
        reply = raw_response
        add_message(chat_id, "assistant", raw_response)

    await update.message.reply_text(reply)


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /stats command – show usage dashboard."""
    info = get_stats()
    recent = get_recent_interactions(5)

    lines = [
        "📊 AI-PASS Stats",
        f"  Total interactions: {info['total_interactions']}",
        f"  Active users: {info['active_users']}",
        "",
        "🕑 Last 5 interactions:",
    ]
    if recent:
        for i in recent:
            lines.append(f"  [{i['role']}] {i['content']}")
    else:
        lines.append("  No interactions yet.")

    await update.message.reply_text("\n".join(lines))


def main() -> None:

    if not TELEGRAM_BOT_TOKEN:
        logger.warning("TELEGRAM_BOT_TOKEN not set – running dry-run smoke test instead.")
        if not OPENAI_API_KEY:
            logger.warning("OPENAI_API_KEY not set – pipeline will use fallback error handling.")
        result = orchestrator.handle("hello world")
        print(f"Smoke test passed. Orchestrator returned:\n{result}")
        sys.exit(0)

    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Bot is starting...")
    app.run_polling()


if __name__ == "__main__":
    main()
