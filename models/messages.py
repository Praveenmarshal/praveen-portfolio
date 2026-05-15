"""models/messages.py — Contact form messages model"""
from database.db import get_collection, ts_now


def save_message(name: str, email: str, message: str, ip: str = "") -> dict:
    col = get_collection("messages")
    doc = {
        "name":       name,
        "email":      email,
        "message":    message,
        "ip":         ip,
        "read":       False,
        "created_at": ts_now(),
    }
    result = col.insert_one(doc)
    doc["_id"] = str(result.inserted_id)
    return doc


def get_messages(limit: int = 50) -> list:
    col = get_collection("messages")
    try:
        return [
            {**m, "_id": str(m["_id"])}
            for m in col.find().sort("created_at", -1).limit(limit)
        ]
    except Exception:
        return list(col.find())


def count_messages() -> int:
    return get_collection("messages").count_documents({})


def mark_read(msg_id: str):
    from bson import ObjectId
    col = get_collection("messages")
    try:
        col.update_one({"_id": ObjectId(msg_id)}, {"$set": {"read": True}})
    except Exception:
        pass
