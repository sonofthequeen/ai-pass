import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///ai_pass.db")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
