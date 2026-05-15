"""routes/chatbot.py — AI Chatbot API with Gemini + conversation memory"""

import os
import uuid
import logging
from datetime import datetime, timezone
from flask import Blueprint, request, jsonify, Response, stream_with_context
from database.db import get_collection, ts_now

logger = logging.getLogger(__name__)
chatbot_bp = Blueprint("chatbot", __name__)

# ── Portfolio context (injected into every Gemini prompt) ─────────────────
PORTFOLIO_CONTEXT = """
You are an AI assistant for Praveen K's portfolio website. Answer ONLY about Praveen K.

PERSONAL INFO:
- Full Name: Praveen K
- Role: Data Analyst (Fresher) | B.Tech AI & Data Science student
- College: Vetri Vinayaha College of Engineering and Technology, Trichy, Tamil Nadu
- Graduating: 2026
- Email: praveenkicha01@gmail.com
- Phone: +91 8825870266
- LinkedIn: linkedin.com/in/praveen-kannan-6862382a2
- GitHub: github.com/praveenmarshal
- Location: Trichy, Tamil Nadu, India

CORE SKILLS:
- Python (Pandas, NumPy) — 90%
- SQL — 88%
- MS Excel (Advanced) — 92%
- Power BI — 93%
- Tableau — 80%
- EDA & Statistical Analysis, Machine Learning fundamentals, Data Modelling, KPI Analysis

INTERNSHIP EXPERIENCE:
1. Data Analytics Intern — Solutions Pro Company, Trichy (Jun 2024 – Aug 2024)
   - Cleaned datasets with SQL, built Power BI dashboards, performed EDA
2. Python Intern — Solutions Pro Company, Trichy (Jan 2025 – May 2025)
   - Data analysis with Python/SQL, built Power BI reports, automated workflows

PROJECTS (8 total):
1. Smartphone Market Analysis 2018–2026 (Python, SQL, Power BI) — 15+ brands, CAGR analysis
2. Nykaa Campaign Intelligence Hub (Power BI, DAX) — 55K+ records, 6 channels
3. Customer Churn Analysis (SQL, Power BI) — 68% churn probability model
4. Nassau Candy Profitability Dashboard (Python, Streamlit, Plotly) — live analytics
5. Retail Sales Analysis Dashboard (SQL, Power BI) — multi-page BI
6. Pizza Sales Analytics Dashboard (SQL, Power BI) — KPI-driven
7. Cricket Player Analysis Dashboard (Power BI, DAX) — ODI, T20, Test formats
8. Tamil Movie Recommendation System (Python, TMDb API, Pandas) — weighted IMDb ranking

PERSONALITY TRAITS: Detail-oriented, analytical thinker, quick learner, team player.

RESPONSE RULES:
- Be friendly, concise, and professional
- Use bullet points for lists
- For unrelated questions, politely redirect to Praveen's portfolio
- Keep responses under 200 words unless asked for details
- Add relevant emojis sparingly
"""


def _log_conversation(session_id: str, role: str, content: str):
    """Persist chat messages for analytics & admin viewing."""
    try:
        col = get_collection("chat_logs")
        col.insert_one({
            "session_id": session_id,
            "role":       role,
            "content":    content,
            "created_at": ts_now(),
        })
    except Exception as e:
        logger.debug("Chat log error: %s", e)


def _get_history(session_id: str, limit: int = 10) -> list:
    """Fetch last N messages for conversation memory."""
    try:
        col = get_collection("chat_logs")
        docs = list(col.find({"session_id": session_id}).sort("created_at", -1).limit(limit))
        docs.reverse()
        return [{"role": d["role"], "parts": [d["content"]]} for d in docs]
    except Exception:
        return []


def _call_gemini(message: str, history: list) -> str:
    """Call Gemini API and return the text response."""
    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key:
        return _local_fallback(message)

    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)

        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=PORTFOLIO_CONTEXT,
        )

        # Build Gemini-format history
        gemini_history = []
        for h in history:
            gemini_history.append({
                "role":  h["role"],
                "parts": h["parts"],
            })

        chat = model.start_chat(history=gemini_history)
        response = chat.send_message(message)
        return response.text

    except Exception as e:
        logger.error("Gemini API error: %s", e)
        return _local_fallback(message)


def _local_fallback(text: str) -> str:
    """Keyword-based fallback when Gemini is unavailable."""
    t = text.lower()
    if any(w in t for w in ["about", "who", "yourself", "introduce"]):
        return ("👋 Praveen K is a Data Analyst fresher with a B.Tech in AI & Data Science "
                "(graduating 2026). He specialises in Python, SQL, Power BI, Excel & Tableau. "
                "He has completed 2 internships and 8 real-world projects!")
    if any(w in t for w in ["skill", "tech", "stack", "language"]):
        return ("📊 **Praveen's core skills:**\n• Python (Pandas, NumPy) — 90%\n• SQL — 88%\n"
                "• MS Excel (Advanced) — 92%\n• Power BI — 93%\n• Tableau — 80%\n"
                "• EDA, Statistical Analysis, KPI Design")
    if any(w in t for w in ["project", "work", "portfolio", "built"]):
        return ("🚀 **8 major projects:**\n1. Smartphone Market Analysis\n2. Nykaa Campaign Hub\n"
                "3. Customer Churn Analysis\n4. Nassau Candy Dashboard\n5. Retail Sales BI\n"
                "6. Pizza Sales Analytics\n7. Cricket Player Dashboard\n8. Tamil Movie Recommender")
    if any(w in t for w in ["contact", "email", "phone", "reach", "hire"]):
        return "📧 praveenkicha01@gmail.com\n📱 +91 8825870266\n🔗 linkedin.com/in/praveen-kannan-6862382a2"
    if any(w in t for w in ["experience", "intern", "job", "work"]):
        return ("💼 **Internships:**\n• Python Intern @ Solutions Pro (Jan–May 2025)\n"
                "• Data Analytics Intern @ Solutions Pro (Jun–Aug 2024)\nBoth in Trichy, TN.")
    if any(w in t for w in ["education", "college", "degree", "study"]):
        return "🎓 B.Tech in AI & Data Science — Vetri Vinayaha College of Engineering and Technology (2026)"
    if any(w in t for w in ["hi", "hello", "hey", "greet"]):
        return "👋 Hi! I'm Praveen's AI assistant. Ask me about his skills, projects, experience, or contact info!"
    if any(w in t for w in ["resume", "cv", "download"]):
        return "📄 You can download Praveen's resume from the **Resume** section on this page!"
    return ("🤔 Great question! For more details, feel free to reach Praveen directly at "
            "praveenkicha01@gmail.com or via the Contact section.")


# ── Routes ─────────────────────────────────────────────────────────────────

@chatbot_bp.route("/chat", methods=["POST"])
def chat():
    data       = request.get_json(silent=True) or {}
    message    = (data.get("message") or "").strip()
    session_id = data.get("session_id") or str(uuid.uuid4())

    if not message:
        return jsonify({"error": "Message is required"}), 400
    if len(message) > 1000:
        return jsonify({"error": "Message too long (max 1000 chars)"}), 400

    # Track analytics
    try:
        from models.analytics import track_event
        track_event("chatbot_message", {"session": session_id},
                    ip=request.remote_addr, ua=request.user_agent.string)
    except Exception:
        pass

    # Retrieve conversation history
    history = _get_history(session_id)

    # Log user message
    _log_conversation(session_id, "user", message)

    # Generate AI response
    reply = _call_gemini(message, history)

    # Log bot message
    _log_conversation(session_id, "model", reply)

    return jsonify({
        "reply":      reply,
        "session_id": session_id,
        "timestamp":  ts_now().isoformat(),
    })


@chatbot_bp.route("/chat/stream", methods=["POST"])
def chat_stream():
    """Streaming endpoint — uses SSE (Server-Sent Events)."""
    data       = request.get_json(silent=True) or {}
    message    = (data.get("message") or "").strip()
    session_id = data.get("session_id") or str(uuid.uuid4())

    if not message:
        return jsonify({"error": "Message is required"}), 400

    api_key = os.getenv("GEMINI_API_KEY", "")

    def generate():
        if not api_key:
            reply = _local_fallback(message)
            # Simulate streaming
            for word in reply.split(" "):
                yield f"data: {word} \n\n"
            yield "data: [DONE]\n\n"
            return

        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                system_instruction=PORTFOLIO_CONTEXT,
            )
            history = _get_history(session_id)
            gemini_history = [{"role": h["role"], "parts": h["parts"]} for h in history]
            chat = model.start_chat(history=gemini_history)
            _log_conversation(session_id, "user", message)
            full_reply = []
            response = chat.send_message(message, stream=True)
            for chunk in response:
                if chunk.text:
                    full_reply.append(chunk.text)
                    yield f"data: {chunk.text}\n\n"
            _log_conversation(session_id, "model", "".join(full_reply))
            yield "data: [DONE]\n\n"
        except Exception as e:
            logger.error("Stream error: %s", e)
            yield f"data: {_local_fallback(message)}\n\n"
            yield "data: [DONE]\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={
            "Cache-Control":               "no-cache",
            "X-Accel-Buffering":           "no",
            "Access-Control-Allow-Origin": "*",
        },
    )


@chatbot_bp.route("/chat/history/<session_id>", methods=["GET"])
def get_chat_history(session_id: str):
    try:
        col  = get_collection("chat_logs")
        docs = list(col.find({"session_id": session_id}).sort("created_at", 1))
        msgs = [{"role": d["role"], "content": d["content"],
                 "time": d["created_at"].isoformat() if hasattr(d["created_at"], "isoformat") else str(d["created_at"])}
                for d in docs]
        return jsonify({"messages": msgs, "session_id": session_id})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
