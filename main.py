"""AI-PASS – Telegram bot entry point."""

import json
import logging
import sys

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

from config import TELEGRAM_BOT_TOKEN, OPENAI_API_KEY
from memory import add_message, get_history
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

    # Get structured response from orchestrator (with chat context)
    # NOTE: store user message AFTER getting history so the current message
    # isn't duplicated (orchestrator already passes it as user_message).
    raw_response = orchestrator.handle(user_text, chat_id)

    # Store user message
    add_message(chat_id, "user", user_text)

    # Format for Telegram
    try:
        data = json.loads(raw_response)
        reply = (
            f"📋 {data.get('summary', '')}\n"
            f"⚡ Priority: {data.get('priority', 'medium')}\n"
            f"➡️ Action: {data.get('action', '')}"
        )
        # Store the clean summary in memory (not the emoji-formatted text)
        add_message(chat_id, "assistant", data.get("summary", raw_response))
    except (json.JSONDecodeError, TypeError):
        reply = raw_response
        add_message(chat_id, "assistant", raw_response)

    await update.message.reply_text(reply)


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
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Bot is starting...")
    app.run_polling()


if __name__ == "__main__":
    main()
