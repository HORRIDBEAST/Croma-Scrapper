import feedparser
import redis
import json
import logging
from datetime import datetime
import time

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

COMPANIES = [
    "Pfizer", "Novartis", "Sanofi", "Takeda", "Merck",
    "Bayer", "AbbVie", "Bristol Myers Squibb", "Johnson & Johnson",
    "Roche", "Eli Lilly", "AstraZeneca", "Amgen"
]

COMPANY_COLORS = {
    "Pfizer": "#0093D0", "Novartis": "#EC0016", "Sanofi": "#7B2D8B",
    "Takeda": "#E4002B", "Merck": "#009B77", "Bayer": "#10A0E3",
    "AbbVie": "#071D49", "Bristol Myers Squibb": "#003865",
    "Johnson & Johnson": "#CC0000", "Roche": "#0066CC",
    "Eli Lilly": "#D52B1E", "AstraZeneca": "#830051", "Amgen": "#002A5C"
}

CATEGORY_KEYWORDS = {
    "Drug Launch": ["launch", "launched", "approved", "approval", "fda approved", "new drug", "marketed", "clearance", "nda", "bla"],
    "Innovation": ["discovery", "breakthrough", "innovation", "research", "clinical trial", "phase 1", "phase 2", "phase 3", "study", "data", "results"],
    "Events": ["conference", "event", "summit", "webinar", "meeting", "symposium", "congress", "asco", "aha", "esc"],
    "Acquisition": ["acquisition", "acquires", "merger", "deal", "partnership", "collaboration", "agreement", "license"],
    "Earnings": ["earnings", "revenue", "quarterly", "financial results", "q1", "q2", "q3", "q4", "guidance"]
}

def categorize(title, summary=""):
    text = (title + " " + summary).lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        if any(kw in text for kw in keywords):
            return category
    return "General"

def scrape_pharma_news():
    all_news = []
    seen_links = set()

    for company in COMPANIES:
        logging.info(f"Scraping news for: {company}")
        query = company.replace(" ", "+") + "+pharmaceutical+drug"
        rss_url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"

        try:
            feed = feedparser.parse(rss_url)
            count = 0

            for entry in feed.entries:
                link = entry.get("link", "")
                if link in seen_links:
                    continue
                seen_links.add(link)

                title = entry.get("title", "No title")
                summary = entry.get("summary", "")

                # Clean up summary (Google News adds HTML sometimes)
                import re
                summary = re.sub(r'<[^>]+>', '', summary).strip()

                published_raw = entry.get("published", "")
                try:
                    from email.utils import parsedate_to_datetime
                    dt = parsedate_to_datetime(published_raw)
                    published = dt.strftime("%b %d, %Y %I:%M %p")
                    timestamp = dt.timestamp()
                except:
                    published = published_raw
                    timestamp = time.time()

                source = ""
                if hasattr(entry, "source") and entry.source:
                    source = entry.source.get("title", "")
                if not source and " - " in title:
                    source = title.rsplit(" - ", 1)[-1]
                    title = title.rsplit(" - ", 1)[0]

                news_item = {
                    "id": f"{company}_{count}_{int(timestamp)}",
                    "company": company,
                    "company_color": COMPANY_COLORS.get(company, "#333333"),
                    "title": title.strip(),
                    "summary": summary[:300] + "..." if len(summary) > 300 else summary,
                    "link": link,
                    "published": published,
                    "timestamp": timestamp,
                    "source": source,
                    "category": categorize(title, summary)
                }

                all_news.append(news_item)
                count += 1

                if count >= 6:  # Max 6 articles per company
                    break

            logging.info(f"  → {count} articles found for {company}")
            time.sleep(0.5)  # polite delay between companies

        except Exception as e:
            logging.error(f"Error scraping {company}: {e}")
            continue

    # Sort by most recent first
    all_news.sort(key=lambda x: x.get("timestamp", 0), reverse=True)
    logging.info(f"Total articles scraped: {len(all_news)}")
    return all_news


if __name__ == "__main__":
    try:
        r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        r.ping()
        logging.info("Redis connected.")
    except redis.ConnectionError:
        logging.error("Redis not running! Start Redis first.")
        exit(1)

    news_data = scrape_pharma_news()

    if news_data:
        r.set("pharma_news", json.dumps(news_data))
        r.set("pharma_last_updated", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        logging.info(f"Stored {len(news_data)} articles in Redis under 'pharma_news'")
    else:
        logging.warning("No news data scraped.")

    logging.info("Pharma scraper finished.")