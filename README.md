# AI-PASS

AI-powered Personal Assistant System with Telegram bot interface.

## Setup

1. Copy `.env.example` to `.env` and fill in your credentials:
   ```
   cp .env.example .env
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the bot:
   ```
   python main.py
   ```

## Project Structure

```
ai-pass/
├── main.py              # Entry point – starts the Telegram bot
├── config.py            # Loads environment variables
├── db.py                # Database helpers
├── memory.py            # Conversation memory store
├── models.py            # Data models
├── agent/
│   ├── orchestrator.py  # Routes user messages to the right tool
│   ├── planner.py       # Breaks tasks into steps
│   └── evaluator.py     # Evaluates tool outputs
└── tools/
    ├── base.py           # Base tool interface
    ├── text_processor.py # Text processing tool
    ├── classifier.py     # Intent classifier tool
    └── action_tool.py    # Action execution tool
```
