"""models/projects.py — Projects model (DB-backed with static fallback)"""
from database.db import get_collection, ts_now

# ── Default projects (static fallback / seed data) ─────────────────────────

DEFAULT_PROJECTS = [
    {
        "id": "smartphone-market",
        "order": 1,
        "title": "Smartphone Market Analysis 2018–2026",
        "tags": ["Python", "SQL", "Power BI"],
        "description": "Engineered preprocessing & transformation workflows in Python/SQL to analyse longitudinal smartphone sales data across 15+ brands. Identified that mid-range segment CAGR outpaced premium by 12%, informing a go-to-market insight report.",
        "metrics": [{"val": "15+", "label": "Brands"}, {"val": "12%", "label": "CAGR Delta"}, {"val": "2026", "label": "Forecast"}],
        "image": "https://images.pexels.com/photos/6956903/pexels-photo-6956903.jpeg?auto=compress&cs=tinysrgb&fit=crop&h=627&w=1200",
        "github": "https://github.com/praveenmarshal",
        "live": "",
        "featured": True,
    },
    {
        "id": "nykaa-campaign",
        "order": 2,
        "title": "Nykaa Campaign Intelligence Hub",
        "tags": ["Power BI", "DAX", "Marketing Analytics"],
        "description": "Processed and analysed 55,000+ marketing records across 6 channels. Designed a multi-page Power BI dashboard to track ROI, CTR, and campaign performance. Email + influencer channels contributed 61% of total revenue at lowest acquisition cost.",
        "metrics": [{"val": "55K+", "label": "Records"}, {"val": "6", "label": "Channels"}, {"val": "61%", "label": "Revenue Share"}],
        "image": "https://images.pexels.com/photos/7947568/pexels-photo-7947568.jpeg?auto=compress&cs=tinysrgb&fit=crop&h=627&w=1200",
        "github": "https://github.com/praveenmarshal",
        "live": "",
        "featured": True,
    },
    {
        "id": "customer-churn",
        "order": 3,
        "title": "Customer Churn Analysis",
        "tags": ["SQL", "Power BI", "DAX"],
        "description": "Analysed customer behavioural data to compute churn risk scores. Identified high-risk segment (≤6 months tenure with no add-ons) with 68% churn probability, enabling targeted retention strategies.",
        "metrics": [{"val": "68%", "label": "Churn Prob."}, {"val": "DAX", "label": "Measures"}, {"val": "Risk", "label": "Segmentation"}],
        "image": "https://images.pexels.com/photos/590022/pexels-photo-590022.jpeg?auto=compress&cs=tinysrgb&fit=crop&h=627&w=1200",
        "github": "https://github.com/praveenmarshal",
        "live": "",
        "featured": True,
    },
    {
        "id": "nassau-candy",
        "order": 4,
        "title": "Nassau Candy Profitability Dashboard",
        "tags": ["Python", "Streamlit", "Plotly"],
        "description": "Developed a live Streamlit analytics dashboard for Nassau Candy Distributor to analyze product profitability and division performance. Built interactive visualizations for cost diagnostics, Pareto analysis, and factory-level insights.",
        "metrics": [{"val": "Live", "label": "Dashboard"}, {"val": "Pareto", "label": "Analysis"}, {"val": "Plotly", "label": "Charts"}],
        "image": "https://images.pexels.com/photos/1323550/pexels-photo-1323550.jpeg?auto=compress&cs=tinysrgb&fit=crop&h=627&w=1200",
        "github": "https://github.com/praveenmarshal",
        "live": "",
        "featured": False,
    },
    {
        "id": "retail-sales",
        "order": 5,
        "title": "Retail Sales Analysis Dashboard",
        "tags": ["SQL", "Power BI", "Analytics"],
        "description": "Created a multi-page retail sales analytics dashboard to evaluate product performance, outlet efficiency, and sales distribution. Performed advanced SQL analysis using aggregation and window functions.",
        "metrics": [{"val": "Multi", "label": "Pages"}, {"val": "SQL", "label": "Advanced"}, {"val": "10+", "label": "Outlets"}],
        "image": "https://images.pexels.com/photos/3962285/pexels-photo-3962285.jpeg?auto=compress&cs=tinysrgb&fit=crop&h=627&w=1200",
        "github": "https://github.com/praveenmarshal",
        "live": "",
        "featured": False,
    },
    {
        "id": "pizza-sales",
        "order": 6,
        "title": "Pizza Sales Analytics Dashboard",
        "tags": ["SQL", "Power BI", "KPI"],
        "description": "Designed an interactive BI dashboard to analyze pizza sales trends, customer ordering behavior, revenue distribution, and product performance. KPI-driven visualizations identify best-selling and low-performing products.",
        "metrics": [{"val": "KPI", "label": "Driven"}, {"val": "Trend", "label": "Analysis"}, {"val": "BI", "label": "Dashboard"}],
        "image": "https://images.pexels.com/photos/905847/pexels-photo-905847.jpeg?auto=compress&cs=tinysrgb&fit=crop&h=627&w=1200",
        "github": "https://github.com/praveenmarshal",
        "live": "",
        "featured": False,
    },
    {
        "id": "cricket-player",
        "order": 7,
        "title": "Cricket Player Analysis Dashboard",
        "tags": ["Power BI", "DAX", "Sports Analytics"],
        "description": "Built an interactive Power BI dashboard to analyze cricket player statistics across ODI, T20, and Test formats. Developed dynamic visualizations for batting/bowling metrics and comparative player insights.",
        "metrics": [{"val": "3", "label": "Formats"}, {"val": "ODI", "label": "T20 · Test"}, {"val": "DAX", "label": "Metrics"}],
        "image": "https://images.pexels.com/photos/10469894/pexels-photo-10469894.jpeg?auto=compress&cs=tinysrgb&fit=crop&h=627&w=1200",
        "github": "https://github.com/praveenmarshal",
        "live": "",
        "featured": False,
    },
    {
        "id": "movie-recommendation",
        "order": 8,
        "title": "Tamil Movie Recommendation System",
        "tags": ["Python", "TMDb API", "Pandas"],
        "description": "Developed a Python-based recommendation system fetching trending Tamil movies using the TMDb API with weighted IMDb-style ranking algorithms implemented using Pandas for real-time recommendations.",
        "metrics": [{"val": "TMDb", "label": "API"}, {"val": "IMDb", "label": "Ranking"}, {"val": "Live", "label": "Real-time"}],
        "image": "https://images.pexels.com/photos/7991579/pexels-photo-7991579.jpeg?auto=compress&cs=tinysrgb&fit=crop&h=627&w=1200",
        "github": "https://github.com/praveenmarshal",
        "live": "",
        "featured": False,
    },
]


def get_projects() -> list:
    col = get_collection("projects")
    try:
        docs = list(col.find().sort("order", 1))
        if docs:
            return [{**d, "_id": str(d["_id"])} for d in docs]
    except Exception:
        pass
    return DEFAULT_PROJECTS


def seed_projects():
    """Insert default projects into DB if collection is empty."""
    col = get_collection("projects")
    try:
        if col.count_documents({}) == 0:
            for p in DEFAULT_PROJECTS:
                p["created_at"] = ts_now()
                col.insert_one(dict(p))
    except Exception:
        pass
