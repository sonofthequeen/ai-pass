"""Conversation memory – keeps recent messages per chat."""

from __future__ import annotations

from datetime import datetime, timezone

_memory: dict[int, list[dict]] = {}
_interactions: list[dict] = []

MAX_HISTORY = 20
MAX_INTERACTIONS = 200


def add_message(chat_id: int, role: str, content: str) -> None:
    """Append a message to the chat history."""
    if chat_id not in _memory:
        _memory[chat_id] = []
    _memory[chat_id].append({"role": role, "content": content})
    # Trim to last MAX_HISTORY messages
    _memory[chat_id] = _memory[chat_id][-MAX_HISTORY:]
    # Track interaction for dashboard
    _interactions.append({
        "chat_id": chat_id,
        "role": role,
        "content": content[:200],
        "timestamp": datetime.now(timezone.utc).isoformat(),
    })
    if len(_interactions) > MAX_INTERACTIONS:
        _interactions[:] = _interactions[-MAX_INTERACTIONS:]


def get_history(chat_id: int) -> list[dict]:
    """Return the message history for a chat."""
    return list(_memory.get(chat_id, []))


def clear_history(chat_id: int) -> None:
    """Clear memory for a chat."""
    _memory.pop(chat_id, None)


def get_all_users() -> list[int]:
    """Return all active chat IDs."""
    return list(_memory.keys())


def get_recent_interactions(n: int = 10) -> list[dict]:
    """Return the last *n* interactions across all users."""
    return list(_interactions[-n:])


def get_stats() -> dict:
    """Return basic usage statistics."""
    return {
        "total_interactions": len(_interactions),
        "active_users": len(_memory),
        "user_ids": list(_memory.keys()),
    }
