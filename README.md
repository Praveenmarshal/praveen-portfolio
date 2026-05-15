# 📊 Praveen K — Full-Stack AI Portfolio Platform

A **production-grade full-stack portfolio** built with Flask, MongoDB Atlas, and Google Gemini AI.
Premium glassmorphism UI with dark/light/emerald/crimson themes, 3D canvas animations, AI chatbot, admin dashboard, and full analytics.

---

## 🏗️ Project Structure

```
portfolio/
├── app.py                 # Flask application factory
├── Procfile               # Gunicorn deployment config
├── runtime.txt            # Python version
├── requirements.txt       # All Python dependencies
├── vercel.json            # Vercel deployment config
├── .env.example           # Environment variables template
├── .gitignore
│
├── static/
│   ├── css/style.css      # Complete glassmorphism CSS (themes, animations, responsive)
│   ├── js/main.js         # Full frontend JS (canvas, chatbot, analytics, forms)
│   ├── images/            # Static images & OG preview
│   ├── icons/             # Favicon assets
│   └── resume/            # PDF resume (optional static backup)
│
├── templates/
│   ├── index.html         # Main portfolio page (Jinja2)
│   └── 404.html           # Custom 404 page
│
├── routes/
│   ├── chatbot.py         # /api/chat, /api/chat/stream, /api/chat/history
│   ├── contact.py         # /api/contact (form submission + email notify)
│   ├── analytics.py       # /api/analytics/track, /api/analytics/stats, /api/projects
│   └── admin.py           # /admin (SPA dashboard), /api/admin/* (JWT-protected)
│
├── models/
│   ├── messages.py        # Contact form messages model
│   ├── analytics.py       # Event analytics model
│   └── projects.py        # Projects model (DB-backed with static fallback)
│
└── database/
    └── db.py              # MongoDB Atlas connection + in-memory fallback
```

---

## ✨ Features

| Category           | What's Included |
|--------------------|-----------------|
| **Frontend**       | Glassmorphism UI, 4 themes, custom cursor, scroll reveal, 3D tilt cards, canvas particles, floating chart animations, responsive |
| **AI Chatbot**     | Gemini 1.5 Flash, conversation memory, streaming SSE, typing indicator, quick replies, chat export, session tracking |
| **Backend**        | Flask REST API, JWT auth, rate limiting, CORS, error handling, blueprint architecture |
| **Database**       | MongoDB Atlas with in-memory fallback (zero-config dev mode) |
| **Analytics**      | Page views, resume downloads, chatbot opens, project views, section tracking |
| **Admin Dashboard**| Hidden `/admin` SPA, JWT login, real-time stats, message inbox, chat log viewer |
| **Contact Form**   | Backend validation, spam detection, MongoDB storage, email notification (optional SMTP) |
| **SEO**            | OG tags, Twitter cards, JSON-LD schema, sitemap.xml, robots.txt, canonical URLs |
| **Deployment**     | Procfile, runtime.txt, vercel.json, environment variables, gunicorn config |
| **Security**       | Rate limiting, JWT tokens, input sanitisation, CORS protection, .env secrets |

---

## 🚀 Quick Start

### 1 · Clone & install

```bash
git clone https://github.com/praveenmarshal/portfolio.git
cd portfolio

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### 2 · Configure environment

```bash
cp .env.example .env
# Edit .env and fill in your values
```

**Required variables:**
- `SECRET_KEY` — random 64-char string
- `JWT_SECRET_KEY` — random secret for JWT
- `GEMINI_API_KEY` — from [Google AI Studio](https://aistudio.google.com/)
- `MONGODB_URI` — from [MongoDB Atlas](https://cloud.mongodb.com/) *(optional for local dev)*
- `ADMIN_USERNAME` / `ADMIN_PASSWORD` — for `/admin` login

> **Without MongoDB:** The app runs with an in-memory fallback. Data is lost on restart but everything works locally.

### 3 · Run

```bash
python app.py
```

Visit `http://localhost:5000` · Admin at `http://localhost:5000/admin`

---

## 🔌 API Reference

| Method | Endpoint                      | Auth    | Description                      |
|--------|-------------------------------|---------|----------------------------------|
| POST   | `/api/chat`                   | —       | AI chat (full response)          |
| POST   | `/api/chat/stream`            | —       | AI chat (SSE streaming)          |
| GET    | `/api/chat/history/<session>` | —       | Retrieve chat history            |
| POST   | `/api/contact`                | —       | Submit contact form              |
| POST   | `/api/analytics/track`        | —       | Track frontend events            |
| GET    | `/api/analytics/stats`        | —       | Public aggregate stats           |
| GET    | `/api/projects`               | —       | Fetch projects list              |
| POST   | `/api/admin/login`            | —       | Admin login → JWT token          |
| GET    | `/api/admin/stats`            | JWT     | Full analytics dashboard data    |
| GET    | `/api/admin/messages`         | JWT     | All contact form submissions     |
| GET    | `/api/admin/chats`            | JWT     | All chatbot conversation logs    |
| PATCH  | `/api/admin/messages/<id>/read`| JWT    | Mark message as read             |

---

## ☁️ Deployment

### Render (recommended)
1. Connect GitHub repo → **New Web Service**
2. Runtime: **Python 3**, Build command: `pip install -r requirements.txt`
3. Start command: `gunicorn app:app --bind 0.0.0.0:$PORT`
4. Add all environment variables from `.env.example`

### Railway
1. Connect repo → **Deploy** → set env vars

### Vercel
```bash
npm i -g vercel
vercel --prod
```

---

## 🛡️ Admin Dashboard

Navigate to `/admin` → login with `ADMIN_USERNAME` / `ADMIN_PASSWORD`.

Features:
- Live KPI cards (page views, resume downloads, chatbot stats, contact count)
- Full contact message inbox with read/unread status
- Complete AI chat log viewer by session
- Top viewed projects chart

---

## 🎨 Themes

| Theme    | Accent        | Feel              |
|----------|---------------|-------------------|
| 🌙 Dark  | Purple/Violet | Default, premium  |
| ☀️ Light | Indigo        | Clean, minimal    |
| 💎 Emerald | Cyan/Green  | Futuristic        |
| 🔥 Crimson | Red/Coral   | Bold, energetic   |

Theme preference persists via `localStorage`.

---

## 📝 Personalising

- **Projects**: Edit `models/projects.py → DEFAULT_PROJECTS` or seed MongoDB
- **Chatbot context**: Edit `PORTFOLIO_CONTEXT` in `routes/chatbot.py`
- **Colours/fonts**: Modify CSS variables in `static/css/style.css`
- **Resume PDF**: Drop your PDF at `static/resume/resume.pdf` and update the link

---

*Built with ♥ by Praveen K — Data Analyst · AI & Data Science Enthusiast*
