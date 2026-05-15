"""routes/contact.py — Contact form API with spam protection"""

import re
import os
import logging
from flask import Blueprint, request, jsonify

logger = logging.getLogger(__name__)
contact_bp = Blueprint("contact", __name__)

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _send_email_notification(name: str, email: str, message: str):
    """Send email notification via SMTP (optional)."""
    smtp_host = os.getenv("SMTP_HOST", "")
    smtp_user = os.getenv("SMTP_USER", "")
    smtp_pass = os.getenv("SMTP_PASS", "")
    notify_to = os.getenv("NOTIFY_EMAIL", "praveenkicha01@gmail.com")

    if not all([smtp_host, smtp_user, smtp_pass]):
        logger.info("SMTP not configured — skipping email notification.")
        return

    try:
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart

        msg = MIMEMultipart()
        msg["From"]    = smtp_user
        msg["To"]      = notify_to
        msg["Subject"] = f"[Portfolio] New message from {name}"
        body = f"""
New contact form submission:

Name:    {name}
Email:   {email}
Message: {message}
        """
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP_SSL(smtp_host, 465) as server:
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_user, notify_to, msg.as_string())
        logger.info("Email notification sent.")
    except Exception as e:
        logger.error("Email send failed: %s", e)


def _basic_spam_check(name: str, email: str, message: str) -> bool:
    """Very simple spam heuristics."""
    spam_keywords = ["http://", "https://", "buy now", "click here", "free money",
                     "casino", "crypto", "bitcoin", "SEO", "backlinks"]
    combined = f"{name} {email} {message}".lower()
    return any(kw.lower() in combined for kw in spam_keywords)


@contact_bp.route("/contact", methods=["POST"])
def submit_contact():
    data    = request.get_json(silent=True) or {}
    name    = (data.get("name") or "").strip()
    email   = (data.get("email") or "").strip()
    message = (data.get("message") or "").strip()

    # ── Validation ──────────────────────────────────────────────────────────
    errors = []
    if not name or len(name) < 2:
        errors.append("Name must be at least 2 characters.")
    if not email or not EMAIL_RE.match(email):
        errors.append("A valid email is required.")
    if not message or len(message) < 10:
        errors.append("Message must be at least 10 characters.")
    if len(message) > 3000:
        errors.append("Message is too long (max 3000 chars).")

    if errors:
        return jsonify({"success": False, "errors": errors}), 422

    # ── Spam check ──────────────────────────────────────────────────────────
    if _basic_spam_check(name, email, message):
        logger.warning("Spam detected from %s", request.remote_addr)
        return jsonify({"success": True, "message": "Message received!"}), 200  # Silent discard

    # ── Save to DB ──────────────────────────────────────────────────────────
    try:
        from models.messages import save_message
        save_message(name, email, message, ip=request.remote_addr)
    except Exception as e:
        logger.error("DB save error: %s", e)
        return jsonify({"success": False, "error": "Failed to save message."}), 500

    # ── Analytics ───────────────────────────────────────────────────────────
    try:
        from models.analytics import track_event
        track_event("contact_submit", {"name": name},
                    ip=request.remote_addr, ua=request.user_agent.string)
    except Exception:
        pass

    # ── Email notification ───────────────────────────────────────────────────
    _send_email_notification(name, email, message)

    return jsonify({"success": True, "message": "Your message has been received! I'll get back to you soon 🚀"}), 201


@contact_bp.route("/contact/messages", methods=["GET"])
def get_messages_preview():
    """Public endpoint — only returns count (admin dashboard fetches full list)."""
    try:
        from models.messages import count_messages
        return jsonify({"total_messages": count_messages()})
    except Exception:
        return jsonify({"total_messages": 0})
