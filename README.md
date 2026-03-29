# AI-PASS — Mini AI-Pass Automation Agent

A Telegram-based AI automation assistant built for a 24-hour technical challenge. AI-PASS receives natural-language messages, routes them through a multi-stage agent pipeline, and returns structured, actionable responses — all inside a Telegram chat.

---

## Architecture

The project follows a modular architecture with clear separation of concerns:

```
ai-pass/
├── main.py                # Telegram bot entry point
├── config.py              # Environment variables & OpenAI client
├── db.py                  # In-memory database helpers
├── memory.py              # Per-user conversation memory & stats
├── models.py              # Data models (Message, Plan, ToolResult)
├── agent/
│   ├── orchestrator.py    # Central pipeline coordinator
│   ├── planner.py         # LLM-powered planning module
│   └── evaluator.py       # LLM-powered evaluation & structured output
├── tools/
│   ├── base.py            # Abstract base class for tools
│   ├── classifier.py      # Intent classification tool
│   ├── text_processor.py  # Text summarisation tool
│   └── action_tool.py     # Action suggestion tool
├── Dockerfile             # Container image for deployment
└── requirements.txt       # Python dependencies
```

| Layer | Responsibility |
|-------|---------------|
| **Telegram interface** (`main.py`) | Receives messages, formats replies, handles `/start` and `/stats` commands |
| **Orchestrator** (`agent/orchestrator.py`) | Runs every message through the 5-stage pipeline |
| **Planner** (`agent/planner.py`) | Decides which tools to invoke and in what order |
| **Evaluator** (`agent/evaluator.py`) | Synthesises tool outputs into a structured JSON response via GPT |
| **Tools** (`tools/`) | Modular units that each perform one task (classify, summarise, suggest) |
| **Memory** (`memory.py`) | Stores conversation history per `chat_id` |
| **Logging** | Python `logging` with `chat_id` tags on every pipeline stage |

---

## Agent Flow

Every incoming message passes through five sequential stages inside the Orchestrator:

```
INTAKE → PLAN → EXECUTE → EVALUATE → DELIVER
```

### 1. Intake
- Receive the user message
- Look up conversation history from memory using the user's `chat_id`

### 2. Plan
- Send the message to the Planner (GPT-based)
- The Planner decides which tools to run and in what order
- Returns a `Plan` object with a list of tools and step descriptions

### 3. Execute
- Run each tool in the planned order
- Collect a `ToolResult` (name, output, success) from every tool

### 4. Evaluate
- Pass the user message, tool results, and conversation history to the Evaluator
- The Evaluator calls GPT to produce a structured JSON response
- Missing fields are filled with safe defaults

### 5. Deliver
- Enrich the evaluator output with pipeline metadata (plan, tools used, memory status, evaluation check)
- Return the full structured response to the Telegram formatter

---

## Tools

All tools extend `BaseTool` and implement a `run(input_text) → ToolResult` method.

| Tool | File | What it does |
|------|------|-------------|
| **Classifier** | `tools/classifier.py` | Classifies the user's intent into one of: `question`, `task`, `greeting`, `feedback`, `other` |
| **Text Processor** | `tools/text_processor.py` | Summarises or clarifies the user's message in 1–2 sentences |
| **Action** | `tools/action_tool.py` | Suggests one concrete, actionable next step the user should take |

Each tool calls OpenAI (`gpt-4o-mini`) independently and returns its output inside a `ToolResult` dataclass.

---

## Memory Design

Conversation memory is stored **in-memory**, keyed by Telegram `chat_id`.

- Each user's history is kept separate — no cross-user data leakage.
- The last 20 messages per user are retained (older messages are trimmed).
- On every message, the Evaluator receives the last 10 messages as conversation context, allowing the agent to maintain continuity across turns.
- A global interaction log (capped at 200 entries) tracks all messages with timestamps and `chat_id` for the `/stats` dashboard.

Memory is **not** persisted to disk — it resets when the process restarts. This is a deliberate simplification for the challenge scope.

---

## Logging Design

Standard Python `logging` is used throughout the pipeline. Every log line from the Orchestrator includes a `[chat=<id>]` tag for traceability.

What is logged at each stage:

| Stage | Logged information |
|-------|--------------------|
| **Intake** | Incoming message received, `chat_id` |
| **Plan** | Tools selected, step descriptions |
| **Execute** | Each tool name and its output |
| **Evaluate** | Full structured response JSON |
| **Deliver** | Completion marker |

Warnings and errors (unknown tools, non-JSON evaluator responses, API failures) are also logged with context.

---

## Structured Output

Every response is a JSON object with two layers:

### Core fields (produced by the Evaluator)

| Field | Type | Description |
|-------|------|-------------|
| `task_type` | string | Type of request: `question`, `task`, `greeting`, `feedback`, `other` |
| `summary` | string | Concise answer to the user |
| `priority` | string | `low`, `medium`, or `high` |
| `suggested_action` | string | Recommended next step |
| `confidence` | float | Model's confidence in the response (0.0–1.0) |

### Agent-flow metadata (added by the Orchestrator)

| Field | Type | Description |
|-------|------|-------------|
| `plan` | list | Steps the planner decided to take |
| `execution_steps` | list | The pipeline stages executed: `["intake", "memory_lookup", "plan", "execute_tools", "evaluate", "deliver"]` |
| `memory_used` | boolean | Whether conversation history was available |
| `tools_used` | list | Each tool's name and output |
| `evaluation` | object | `output_valid` (bool) and `confidence_check` (`"passed"` or `"low"`) |

In Telegram, the response is formatted with emoji labels for readability while the full structured JSON is the internal representation.

---

## What Is Real vs. Mocked

### Fully implemented
- 5-stage agent pipeline (Orchestrator → Planner → Tools → Evaluator → Deliver)
- Three working LLM-powered tools (classifier, text processor, action)
- GPT-based planning (dynamically selects tools per message)
- GPT-based evaluation (produces structured JSON output)
- Per-user conversation memory with context reuse
- Structured output with all required fields + pipeline metadata
- Multi-user support via `chat_id` isolation
- Logging with `chat_id` on all pipeline stages
- `/stats` command for basic usage dashboard
- Telegram bot integration with formatted output
- Dockerfile for containerised deployment

### Simplified / not persisted
- Memory is **in-memory only** (resets on restart) — not backed by SQLite or a database. The `db.py` file contains a generic in-memory store stub but is not used by the main pipeline.
- The `/stats` dashboard is a Telegram command, not a web UI.
- There is no authentication or admin-only access on `/stats`.

Nothing is faked or hardcoded — all tool outputs and evaluations come from live OpenAI API calls.

---

## Setup Instructions

### Prerequisites
- Python 3.11+
- A Telegram bot token (from [@BotFather](https://t.me/BotFather))
- An OpenAI API key

### Installation

```bash
git clone https://github.com/<your-username>/ai-pass.git
cd ai-pass
pip install -r requirements.txt
```

### Environment variables

Create a `.env` file in the project root:

```
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
OPENAI_API_KEY=your-openai-api-key
```

### Run locally

```bash
python main.py
```

If `TELEGRAM_BOT_TOKEN` is not set, the bot runs a dry-run smoke test and exits — useful for verifying the pipeline without Telegram.

---

## Telegram Usage

### Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome message |
| `/stats` | Show total interactions, active users, and last 5 messages |

### Sending messages

Send any text message to the bot. Example inputs:

- `"What is machine learning?"`
- `"Summarise the benefits of remote work"`
- `"I need help planning my week"`
- `"Hello!"`

### Example response

```
🏷 Type: question
📋 Machine learning is a subset of AI where systems learn from data...
⚡ Priority: medium
➡️ Action: Explore an introductory ML course or tutorial.
🎯 Confidence: 0.85

🔧 Agent Flow:
  Plan: classify intent, summarise text, suggest action
  Steps: intake → memory_lookup → plan → execute_tools → evaluate → deliver
  Memory used: no
  Tools:
    • classifier: question
    • text_processor: Machine learning is a branch of AI...
    • action: Explore an introductory ML course or tutorial.
  Eval: valid=True, confidence=passed
```

---

## Deployment Notes

The project includes a `Dockerfile` for containerised deployment:

```bash
docker build -t ai-pass .
docker run --env-file .env ai-pass
```

Intended deployment targets: **Railway**, **Render**, or any platform that supports Docker containers with environment variable configuration. Set `TELEGRAM_BOT_TOKEN` and `OPENAI_API_KEY` as environment variables in the platform dashboard.

---

## Possible Future Improvements

- **Voice input** — accept Telegram voice messages and transcribe via Whisper
- **Persistent storage** — back memory and interaction logs with SQLite or PostgreSQL
- **Richer dashboard** — web-based UI with charts and filtering
- **Stronger planner** — multi-step reasoning with tool chaining and conditional logic
- **More advanced orchestration** — parallel tool execution, retry logic, tool dependencies
- **Better task-type taxonomy** — fine-grained categories with user-configurable labels
- **Admin controls** — restrict `/stats` to authorised users
- **Streaming responses** — send partial replies as the pipeline progresses
