"""
database/db.py — MongoDB Atlas connection & collection helpers
"""

import os
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

_client = None
_db     = None


def get_db():
    """Return the MongoDB database instance (lazy singleton)."""
    global _client, _db

    if _db is not None:
        return _db

    mongo_uri = os.getenv("MONGODB_URI", "")
    db_name   = os.getenv("MONGODB_DB", "praveen_portfolio")

    if not mongo_uri:
        logger.warning("MONGODB_URI not set — running in memory-fallback mode.")
        return None

    try:
        from pymongo import MongoClient
        from pymongo.server_api import ServerApi

        _client = MongoClient(
            mongo_uri,
            server_api=ServerApi("1"),
            serverSelectionTimeoutMS=5000,
        )
        _client.admin.command("ping")          # verify connection
        _db = _client[db_name]

        # Ensure indexes
        _db.messages.create_index("created_at")
        _db.analytics.create_index([("event", 1), ("created_at", -1)])
        _db.chat_logs.create_index("session_id")
        _db.projects.create_index("order")

        logger.info("✅  MongoDB connected → %s", db_name)
        return _db

    except Exception as exc:
        logger.error("MongoDB connection failed: %s", exc)
        return None


def ts_now() -> datetime:
    """Return the current UTC timestamp (timezone-aware)."""
    return datetime.now(timezone.utc)


# ── Convenience wrappers ────────────────────────────────────────────────────

class FallbackCollection:
    """In-memory list that mimics a tiny subset of PyMongo Collection API."""

    def __init__(self):
        self._store = []

    def insert_one(self, doc):
        doc.setdefault("_id", len(self._store) + 1)
        doc.setdefault("created_at", ts_now())
        self._store.append(doc)
        return type("R", (), {"inserted_id": doc["_id"]})()

    def find(self, query=None, **kwargs):
        return list(self._store)

    def find_one(self, query=None):
        return self._store[-1] if self._store else None

    def count_documents(self, query=None):
        return len(self._store)

    def update_one(self, flt, update, upsert=False):
        pass

    def aggregate(self, pipeline):
        return []


_fallback_stores = {}


def get_collection(name: str):
    """Return a real or fallback collection by name."""
    db = get_db()
    if db is not None:
        return db[name]
    if name not in _fallback_stores:
        _fallback_stores[name] = FallbackCollection()
    return _fallback_stores[name]
