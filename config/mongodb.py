import os

from pymongo import MongoClient

_client = None


def get_mongo_client():
    global _client
    if _client is not None:
        return _client

    uri = os.getenv("MONGODB_URI")
    if not uri:
        raise RuntimeError("MONGODB_URI environment variable is not set.")

    _client = MongoClient(uri, serverSelectionTimeoutMS=5000)
    return _client


def get_mongo_db():
    db_name = os.getenv("MONGODB_DB_NAME", "assigntrack")
    return get_mongo_client()[db_name]
