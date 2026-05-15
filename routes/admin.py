"""routes/admin.py — Hidden admin dashboard with JWT authentication"""

import os
import logging
from datetime import datetime, timezone
from functools import wraps
from flask import Blueprint, request, jsonify, render_template_string
from flask_jwt_extended import (
    create_access_token, jwt_required, get_jwt_identity,
    verify_jwt_in_request,
)

logger = logging.getLogger(__name__)
admin_bp = Blueprint("admin", __name__)

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "praveen_admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "change_this_password_in_env")


# ── JWT Login ───────────────────────────────────────────────────────────────

@admin_bp.route("/api/admin/login", methods=["POST"])
def admin_login():
    data     = request.get_json(silent=True) or {}
    username = data.get("username", "")
    password = data.get("password", "")

    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        token = create_access_token(identity=username)
        return jsonify({"token": token, "username": username})
    return jsonify({"error": "Invalid credentials"}), 401


# ── Protected admin API endpoints ──────────────────────────────────────────

@admin_bp.route("/api/admin/stats", methods=["GET"])
@jwt_required()
def admin_stats():
    try:
        from models.analytics import get_stats
        from models.messages  import count_messages
        stats = get_stats()
        stats["total_messages"] = count_messages()
        return jsonify(stats)
    except Exception as e:
        logger.error("Admin stats error: %s", e)
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/api/admin/messages", methods=["GET"])
@jwt_required()
def admin_messages():
    try:
        from models.messages import get_messages
        limit = min(int(request.args.get("limit", 50)), 200)
        return jsonify({"messages": get_messages(limit=limit)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/api/admin/messages/<msg_id>/read", methods=["PATCH"])
@jwt_required()
def mark_message_read(msg_id: str):
    try:
        from models.messages import mark_read
        mark_read(msg_id)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@admin_bp.route("/api/admin/chats", methods=["GET"])
@jwt_required()
def admin_chats():
    try:
        from database.db import get_collection
        col   = get_collection("chat_logs")
        limit = min(int(request.args.get("limit", 100)), 500)
        docs  = list(col.find().sort("created_at", -1).limit(limit))
        return jsonify({
            "chats": [
                {
                    "session_id": d.get("session_id"),
                    "role":       d.get("role"),
                    "content":    d.get("content"),
                    "time":       d["created_at"].isoformat() if hasattr(d.get("created_at"), "isoformat") else "",
                }
                for d in docs
            ]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ── Admin dashboard SPA (self-contained HTML) ───────────────────────────────

ADMIN_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Admin — Praveen Portfolio</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
:root{--bg:#0a0a0f;--bg2:#12121a;--accent:#7c6cf7;--accent2:#b0a8ff;--text:#fff;--text2:#b8b8d0;--glass:rgba(255,255,255,.05);--border:rgba(255,255,255,.12)}
body{font-family:'Segoe UI',sans-serif;background:var(--bg);color:var(--text);min-height:100vh}
#login{display:flex;align-items:center;justify-content:center;height:100vh}
.login-box{background:var(--glass);border:1px solid var(--border);border-radius:20px;padding:48px;width:360px;backdrop-filter:blur(20px)}
.login-box h2{font-size:1.8rem;margin-bottom:8px;background:linear-gradient(135deg,var(--accent),var(--accent2));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.login-box p{color:var(--text2);margin-bottom:32px;font-size:.9rem}
input{width:100%;padding:12px 16px;background:rgba(255,255,255,.08);border:1px solid var(--border);border-radius:10px;color:var(--text);font-size:.9rem;margin-bottom:16px;outline:none;transition:border-color .3s}
input:focus{border-color:var(--accent)}
button{width:100%;padding:12px;background:linear-gradient(135deg,var(--accent),var(--accent2));border:none;border-radius:10px;color:#fff;font-size:.9rem;font-weight:600;cursor:pointer;transition:opacity .3s}
button:hover{opacity:.85}
.error{color:#ff4d6a;font-size:.8rem;margin-bottom:12px}
#dashboard{display:none;padding:32px;max-width:1400px;margin:0 auto}
.dash-header{display:flex;align-items:center;justify-content:space-between;margin-bottom:32px}
.dash-header h1{font-size:1.6rem;background:linear-gradient(135deg,var(--accent),var(--accent2));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.logout-btn{padding:8px 20px;background:rgba(255,77,106,.15);border:1px solid rgba(255,77,106,.4);border-radius:20px;color:#ff4d6a;cursor:pointer;font-size:.8rem;font-weight:600}
.stat-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:20px;margin-bottom:40px}
.stat-card{background:var(--glass);border:1px solid var(--border);border-radius:16px;padding:24px;text-align:center;backdrop-filter:blur(10px)}
.stat-card .num{font-size:2.2rem;font-weight:700;background:linear-gradient(135deg,var(--accent),var(--accent2));-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.stat-card .lbl{font-size:.75rem;color:var(--text2);margin-top:6px;text-transform:uppercase;letter-spacing:1px}
.tabs{display:flex;gap:8px;margin-bottom:24px}
.tab{padding:8px 20px;border-radius:20px;border:1px solid var(--border);background:var(--glass);color:var(--text2);cursor:pointer;font-size:.8rem;transition:all .3s}
.tab.active{background:var(--accent);border-color:var(--accent);color:#fff}
.panel{display:none}
.panel.active{display:block}
.table-wrap{overflow-x:auto}
table{width:100%;border-collapse:collapse;font-size:.85rem}
th{text-align:left;padding:12px 16px;border-bottom:1px solid var(--border);color:var(--text2);font-size:.75rem;text-transform:uppercase;letter-spacing:1px}
td{padding:12px 16px;border-bottom:1px solid rgba(255,255,255,.05);color:var(--text)}
tr:hover td{background:var(--glass)}
.badge{padding:3px 10px;border-radius:10px;font-size:.7rem;font-weight:600}
.badge.unread{background:rgba(124,108,247,.2);color:var(--accent2);border:1px solid rgba(124,108,247,.3)}
.badge.read{background:rgba(0,214,143,.1);color:#00d68f;border:1px solid rgba(0,214,143,.2)}
.badge.user{background:rgba(124,108,247,.2);color:var(--accent2)}
.badge.model{background:rgba(0,214,143,.1);color:#00d68f}
.section-title{font-size:1.1rem;margin-bottom:16px;font-weight:600}
.empty{color:var(--text2);text-align:center;padding:40px;font-size:.9rem}
</style>
</head>
<body>

<!-- LOGIN -->
<div id="login">
  <div class="login-box">
    <h2>Admin Portal</h2>
    <p>Praveen K — Portfolio Dashboard</p>
    <div class="error" id="loginErr"></div>
    <input type="text" id="uname" placeholder="Username">
    <input type="password" id="pwd" placeholder="Password">
    <button onclick="doLogin()">Sign In</button>
  </div>
</div>

<!-- DASHBOARD -->
<div id="dashboard">
  <div class="dash-header">
    <h1>📊 Admin Dashboard</h1>
    <button class="logout-btn" onclick="logout()">Sign Out</button>
  </div>

  <!-- Stats -->
  <div class="stat-grid" id="statGrid"></div>

  <!-- Tabs -->
  <div class="tabs">
    <button class="tab active" onclick="switchTab('messages')">📩 Messages</button>
    <button class="tab" onclick="switchTab('chats')">💬 Chat Logs</button>
    <button class="tab" onclick="switchTab('analytics')">📈 Analytics</button>
  </div>

  <!-- Messages Panel -->
  <div class="panel active" id="panel-messages">
    <div class="table-wrap">
      <table>
        <thead><tr><th>Name</th><th>Email</th><th>Message</th><th>Date</th><th>Status</th></tr></thead>
        <tbody id="messagesBody"></tbody>
      </table>
    </div>
  </div>

  <!-- Chats Panel -->
  <div class="panel" id="panel-chats">
    <div class="table-wrap">
      <table>
        <thead><tr><th>Session</th><th>Role</th><th>Content</th><th>Time</th></tr></thead>
        <tbody id="chatsBody"></tbody>
      </table>
    </div>
  </div>

  <!-- Analytics Panel -->
  <div class="panel" id="panel-analytics">
    <div id="analyticsContent"></div>
  </div>
</div>

<script>
let token = localStorage.getItem('admin_token') || '';

if (token) { showDashboard(); }

async function doLogin() {
  const u = document.getElementById('uname').value;
  const p = document.getElementById('pwd').value;
  const r = await fetch('/api/admin/login', {
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body: JSON.stringify({username:u, password:p})
  });
  const d = await r.json();
  if (r.ok) {
    token = d.token;
    localStorage.setItem('admin_token', token);
    showDashboard();
  } else {
    document.getElementById('loginErr').textContent = d.error || 'Login failed';
  }
}

function logout() {
  localStorage.removeItem('admin_token');
  token = '';
  document.getElementById('dashboard').style.display = 'none';
  document.getElementById('login').style.display = 'flex';
}

async function showDashboard() {
  document.getElementById('login').style.display = 'none';
  document.getElementById('dashboard').style.display = 'block';
  await Promise.all([loadStats(), loadMessages(), loadChats()]);
}

async function apiGet(url) {
  const r = await fetch(url, { headers: {'Authorization': 'Bearer '+token} });
  if (r.status === 401) { logout(); return null; }
  return r.json();
}

async function loadStats() {
  const d = await apiGet('/api/admin/stats');
  if (!d) return;
  const grid = document.getElementById('statGrid');
  const items = [
    {num: d.total_page_views||0, lbl:'Page Views'},
    {num: d.resume_downloads||0, lbl:'Resume Downloads'},
    {num: d.chatbot_opens||0, lbl:'Chatbot Opens'},
    {num: d.chatbot_messages||0, lbl:'Chat Messages'},
    {num: d.contact_submissions||0, lbl:'Contact Submissions'},
    {num: d.total_messages||0, lbl:'Stored Messages'},
  ];
  grid.innerHTML = items.map(i => `
    <div class="stat-card">
      <div class="num">${i.num}</div>
      <div class="lbl">${i.lbl}</div>
    </div>`).join('');
  
  // Analytics tab
  const top = (d.top_projects||[]).map(p => `<li style="margin:6px 0;font-size:.9rem">${p.project}: <b>${p.views}</b> views</li>`).join('');
  document.getElementById('analyticsContent').innerHTML = `
    <div class="section-title">Top Viewed Projects</div>
    <ul style="list-style:none;background:var(--glass);border:1px solid var(--border);border-radius:12px;padding:20px">
      ${top || '<li class="empty">No project views tracked yet.</li>'}
    </ul>
  `;
}

async function loadMessages() {
  const d = await apiGet('/api/admin/messages?limit=50');
  if (!d) return;
  const tbody = document.getElementById('messagesBody');
  if (!d.messages?.length) { tbody.innerHTML = '<tr><td colspan="5" class="empty">No messages yet.</td></tr>'; return; }
  tbody.innerHTML = d.messages.map(m => `
    <tr>
      <td>${esc(m.name)}</td>
      <td>${esc(m.email)}</td>
      <td style="max-width:300px">${esc(m.message.substring(0,120))}${m.message.length>120?'…':''}</td>
      <td style="white-space:nowrap;font-size:.75rem;color:var(--text2)">${fmtDate(m.created_at)}</td>
      <td><span class="badge ${m.read?'read':'unread'}">${m.read?'Read':'New'}</span></td>
    </tr>`).join('');
}

async function loadChats() {
  const d = await apiGet('/api/admin/chats?limit=100');
  if (!d) return;
  const tbody = document.getElementById('chatsBody');
  if (!d.chats?.length) { tbody.innerHTML = '<tr><td colspan="4" class="empty">No chat history yet.</td></tr>'; return; }
  tbody.innerHTML = d.chats.map(c => `
    <tr>
      <td style="font-family:monospace;font-size:.75rem;color:var(--text2)">${c.session_id?.slice(0,8)}…</td>
      <td><span class="badge ${c.role}">${c.role}</span></td>
      <td style="max-width:400px">${esc(c.content?.substring(0,150))}${c.content?.length>150?'…':''}</td>
      <td style="white-space:nowrap;font-size:.75rem;color:var(--text2)">${fmtDate(c.time)}</td>
    </tr>`).join('');
}

function switchTab(name) {
  document.querySelectorAll('.tab').forEach((t,i) => t.classList.toggle('active', ['messages','chats','analytics'][i]===name));
  document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
  document.getElementById('panel-'+name).classList.add('active');
}

function esc(s) { return String(s||'').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }
function fmtDate(s) {
  if (!s) return '—';
  try { return new Date(s).toLocaleString(); } catch { return s; }
}
</script>
</body>
</html>"""


@admin_bp.route("/admin")
def admin_page():
    return ADMIN_HTML
