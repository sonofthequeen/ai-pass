"""Conversation memory – keeps recent messages per chat."""

from __future__ import annotations

_memory: dict[int, list[dict]] = {}

MAX_HISTORY = 20


def add_message(chat_id: int, role: str, content: str) -> None:
    """Append a message to the chat history."""
    if chat_id not in _memory:
        _memory[chat_id] = []
    _memory[chat_id].append({"role": role, "content": content})
    # Trim to last MAX_HISTORY messages
    _memory[chat_id] = _memory[chat_id][-MAX_HISTORY:]


def get_history(chat_id: int) -> list[dict]:
    """Return the message history for a chat."""
    return list(_memory.get(chat_id, []))


def clear_history(chat_id: int) -> None:
    """Clear memory for a chat."""
    _memory.pop(chat_id, None)
