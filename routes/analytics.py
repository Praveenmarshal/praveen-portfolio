"""routes/analytics.py — Event tracking & stats API"""

import logging
from flask import Blueprint, request, jsonify

logger = logging.getLogger(__name__)
analytics_bp = Blueprint("analytics", __name__)

VALID_EVENTS = {
    "page_view", "resume_download", "project_view",
    "chatbot_open", "chatbot_message", "contact_submit",
    "section_view", "theme_change",
}


@analytics_bp.route("/analytics/track", methods=["POST"])
def track():
    data  = request.get_json(silent=True) or {}
    event = (data.get("event") or "").strip()
    meta  = data.get("meta") or {}

    if event not in VALID_EVENTS:
        return jsonify({"error": f"Unknown event '{event}'"}), 400

    try:
        from models.analytics import track_event
        track_event(
            event,
            meta,
            ip=request.remote_addr,
            ua=request.user_agent.string,
        )
        return jsonify({"success": True}), 200
    except Exception as e:
        logger.error("Analytics track error: %s", e)
        return jsonify({"success": False}), 500


@analytics_bp.route("/analytics/stats", methods=["GET"])
def stats():
    """Public stats for the hero section counters, etc."""
    try:
        from models.analytics import get_stats
        s = get_stats()
        # Only expose non-sensitive aggregate data publicly
        return jsonify({
            "total_page_views": s.get("total_page_views", 0),
            "resume_downloads": s.get("resume_downloads", 0),
            "chatbot_opens":    s.get("chatbot_opens", 0),
        })
    except Exception as e:
        logger.error("Stats error: %s", e)
        return jsonify({"total_page_views": 0, "resume_downloads": 0, "chatbot_opens": 0})


@analytics_bp.route("/projects", methods=["GET"])
def get_projects():
    """Return project list for dynamic rendering."""
    try:
        from models.projects import get_projects
        return jsonify({"projects": get_projects()})
    except Exception as e:
        logger.error("Projects error: %s", e)
        return jsonify({"projects": []}), 500
