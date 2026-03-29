"""Simple in-memory database stub."""

_store: dict[str, list[dict]] = {}


def get_collection(name: str) -> list[dict]:
    """Return (or create) a named collection."""
    if name not in _store:
        _store[name] = []
    return _store[name]


def insert(collection: str, record: dict) -> dict:
    """Insert a record into a collection and return it."""
    col = get_collection(collection)
    col.append(record)
    return record


def find_all(collection: str) -> list[dict]:
    """Return all records in a collection."""
    return list(get_collection(collection))
