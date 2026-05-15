"""models/analytics.py — Visitor & event analytics model"""
from database.db import get_collection, ts_now


VALID_EVENTS = {
    "page_view", "resume_download", "project_view",
    "chatbot_open", "chatbot_message", "contact_submit",
    "section_view", "theme_change",
}


def track_event(event: str, meta: dict = None, ip: str = "", ua: str = "") -> bool:
    if event not in VALID_EVENTS:
        return False
    col = get_collection("analytics")
    col.insert_one({
        "event":      event,
        "meta":       meta or {},
        "ip":         ip,
        "user_agent": ua,
        "created_at": ts_now(),
    })
    return True


def get_stats() -> dict:
    col = get_collection("analytics")
    try:
        total_views     = col.count_documents({"event": "page_view"})
        resume_dl       = col.count_documents({"event": "resume_download"})
        chatbot_opens   = col.count_documents({"event": "chatbot_open"})
        chat_messages   = col.count_documents({"event": "chatbot_message"})
        contact_submits = col.count_documents({"event": "contact_submit"})

        # Top projects viewed
        pipeline = [
            {"$match": {"event": "project_view"}},
            {"$group": {"_id": "$meta.project", "count": {"$sum": 1}}},
            {"$sort":  {"count": -1}},
            {"$limit": 5},
        ]
        top_projects = list(col.aggregate(pipeline))

        # Events over last 7 days
        from datetime import timedelta, timezone, datetime
        cutoff = datetime.now(timezone.utc) - timedelta(days=7)
        recent_pipeline = [
            {"$match": {"created_at": {"$gte": cutoff}, "event": "page_view"}},
            {"$group": {
                "_id": {
                    "$dateToString": {"format": "%Y-%m-%d", "date": "$created_at"}
                },
                "count": {"$sum": 1},
            }},
            {"$sort": {"_id": 1}},
        ]
        daily_views = list(col.aggregate(recent_pipeline))

        return {
            "total_page_views":    total_views,
            "resume_downloads":    resume_dl,
            "chatbot_opens":       chatbot_opens,
            "chatbot_messages":    chat_messages,
            "contact_submissions": contact_submits,
            "top_projects":        [{"project": p["_id"], "views": p["count"]} for p in top_projects],
            "daily_views":         [{"date": d["_id"], "views": d["count"]} for d in daily_views],
        }

    except Exception:
        # Fallback for in-memory store
        docs = list(col.find())
        return {
            "total_page_views":    sum(1 for d in docs if d.get("event") == "page_view"),
            "resume_downloads":    sum(1 for d in docs if d.get("event") == "resume_download"),
            "chatbot_opens":       sum(1 for d in docs if d.get("event") == "chatbot_open"),
            "chatbot_messages":    sum(1 for d in docs if d.get("event") == "chatbot_message"),
            "contact_submissions": sum(1 for d in docs if d.get("event") == "contact_submit"),
            "top_projects":        [],
            "daily_views":         [],
        }
