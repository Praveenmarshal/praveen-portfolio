"""
Praveen K — Data Analyst Portfolio
Full-Stack Flask Application
"""

import os
from datetime import timedelta
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv

load_dotenv()


def create_app():
    app = Flask(__name__)

    # ── Configuration ──────────────────────────────────────────────────────────
    app.config["SECRET_KEY"]         = os.getenv("SECRET_KEY", "change-me-in-production")
    app.config["JWT_SECRET_KEY"]     = os.getenv("JWT_SECRET_KEY", "jwt-change-me-in-production")
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=12)
    app.config["JSON_SORT_KEYS"]     = False

    # ── Extensions ─────────────────────────────────────────────────────────────
    CORS(app, resources={r"/api/*": {"origins": os.getenv("ALLOWED_ORIGINS", "*")}})
    JWTManager(app)

    limiter = Limiter(
        app=app,
        key_func=get_remote_address,
        default_limits=["300 per day", "60 per hour"],
        storage_uri=os.getenv("REDIS_URL", "memory://"),
    )

    # ── Blueprints ─────────────────────────────────────────────────────────────
    from routes.chatbot   import chatbot_bp
    from routes.contact   import contact_bp
    from routes.analytics import analytics_bp
    from routes.admin     import admin_bp

    app.register_blueprint(chatbot_bp,   url_prefix="/api")
    app.register_blueprint(contact_bp,   url_prefix="/api")
    app.register_blueprint(analytics_bp, url_prefix="/api")
    app.register_blueprint(admin_bp)

    # ── Main routes ────────────────────────────────────────────────────────────
    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/sitemap.xml")
    def sitemap():
        from flask import Response
        xml = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url><loc>https://praveenk.dev/</loc><priority>1.0</priority></url>
</urlset>"""
        return Response(xml, mimetype="application/xml")

    @app.route("/robots.txt")
    def robots():
        from flask import Response
        txt = "User-agent: *\nAllow: /\nDisallow: /admin\nSitemap: /sitemap.xml"
        return Response(txt, mimetype="text/plain")

    # ── Error handlers ─────────────────────────────────────────────────────────
    @app.errorhandler(404)
    def not_found(e):
        if request.path.startswith("/api/"):
            return jsonify({"error": "Endpoint not found"}), 404
        return render_template("404.html"), 404

    @app.errorhandler(429)
    def rate_limited(e):
        return jsonify({"error": "Too many requests. Please slow down."}), 429

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"error": "Internal server error"}), 500

    return app


app = create_app()

if __name__ == "__main__":
    port  = int(os.getenv("PORT", 5000))
    debug = os.getenv("FLASK_ENV", "development") != "production"
    app.run(host="0.0.0.0", port=port, debug=debug)
