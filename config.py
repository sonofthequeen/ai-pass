import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///ai_pass.db")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

MODEL = "gpt-4o-mini"

_client: OpenAI | None = None


def get_openai_client() -> OpenAI:
    """Return a shared OpenAI client instance."""
    global _client
    if _client is None:
        _client = OpenAI(api_key=OPENAI_API_KEY)
    return _client
