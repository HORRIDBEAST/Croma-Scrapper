from flask import Flask, jsonify, request
from flask_cors import CORS
import redis
import json
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:8080"}})

try:
    r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    r.ping()
    logging.info("Redis connected.")
except redis.ConnectionError as e:
    logging.error(f"Redis connection failed: {e}")
    r = None


@app.route("/news", methods=["GET"])
def get_news():
    if not r:
        return jsonify({"error": "Redis not connected"}), 503

    company = request.args.get("company", "").strip()
    category = request.args.get("category", "").strip()
    search = request.args.get("search", "").strip().lower()

    try:
        news_json = r.get("pharma_news")
        if not news_json:
            return jsonify({"message": "No data found. Run pharma_scraper.py first."}), 404

        news = json.loads(news_json)

        # Filters
        if company and company != "All":
            news = [n for n in news if n["company"] == company]
        if category and category != "All":
            news = [n for n in news if n["category"] == category]
        if search:
            news = [n for n in news if search in n["title"].lower() or search in n["summary"].lower()]

        last_updated = r.get("pharma_last_updated") or "Unknown"
        return jsonify({"news": news, "count": len(news), "last_updated": last_updated})

    except Exception as e:
        logging.error(f"Error in /news: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/companies", methods=["GET"])
def get_companies():
    companies = [
        "Pfizer", "Novartis", "Sanofi", "Takeda", "Merck",
        "Bayer", "AbbVie", "Bristol Myers Squibb", "Johnson & Johnson",
        "Roche", "Eli Lilly", "AstraZeneca", "Amgen"
    ]
    return jsonify(companies)


@app.route("/refresh", methods=["POST"])
def refresh_news():
    """Trigger a fresh scrape on demand."""
    try:
        import subprocess
        import sys
        subprocess.Popen([sys.executable, "pharma_scraper.py"])
        return jsonify({"message": "Scraper triggered. Check back in ~30 seconds."})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/", methods=["GET"])
def health():
    return jsonify({"status": "healthy", "service": "Pharma News API", "port": 5001})


if __name__ == "__main__":
    app.run(debug=True, port=5001)