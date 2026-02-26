import os
from datetime import datetime, timezone

_client = None


def get_mongo_client():
    global _client
    if _client is not None:
        return _client

    uri = os.getenv("MONGODB_URI")
    if not uri:
        raise RuntimeError("MONGODB_URI environment variable is not set.")

    try:
        from pymongo import MongoClient
    except ImportError as exc:
        raise RuntimeError("pymongo is not installed.") from exc

    _client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    return _client


def get_mongo_db():
    db_name = os.getenv("MONGODB_DB_NAME", "assigntrack")
    return get_mongo_client()[db_name]


def log_event(event_type, payload):
    uri = os.getenv("MONGODB_URI")
    if not uri:
        return False

    try:
        db = get_mongo_db()
        db.activity_logs.insert_one(
            {
                "event_type": event_type,
                "payload": payload,
                "created_at": datetime.now(timezone.utc),
            }
        )
        return True
    except Exception:
        # Mongo logging must never break app requests.
        return False
