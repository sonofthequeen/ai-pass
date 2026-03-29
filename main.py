"""AI-PASS – Telegram bot entry point."""

import logging
import sys

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

from config import TELEGRAM_BOT_TOKEN
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

    # Store user message
    add_message(chat_id, "user", user_text)

    # Get response from orchestrator
    response = orchestrator.handle(user_text)

    # Store assistant response
    add_message(chat_id, "assistant", response)

    await update.message.reply_text(response)


def main() -> None:
    if not TELEGRAM_BOT_TOKEN:
        logger.warning("TELEGRAM_BOT_TOKEN not set – running dry-run smoke test instead.")
        # Smoke test: make sure all imports and orchestrator work
        result = orchestrator.handle("hello world")
        print(f"Smoke test passed. Orchestrator returned: {result}")
        sys.exit(0)

    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Bot is starting...")
    app.run_polling()


if __name__ == "__main__":
    main()
