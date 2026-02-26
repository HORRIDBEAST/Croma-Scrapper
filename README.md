# Full Stack Intelligence Dashboard

A dual-module full stack web application built with **Python (Flask)** + **Vue.js** that combines:

1. **Croma Electronics Store** — scrapes live product data from Croma's TV & Accessories catalogue and displays a fully filterable product grid.
2. **Pharma Intelligence Feed** — scrapes real-time pharmaceutical news (via Google News RSS) for 13 major pharma companies and displays a categorised, searchable news dashboard.

Both apps share a single Vue frontend (SPA with Vue Router), two independent Flask backends, and a shared Redis instance for caching.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────┐
│               Browser: localhost:8080            │
│                                                  │
│   /          →  Croma Electronics Store          │
│   /pharma    →  Pharma Intelligence Feed         │
└──────────────────────┬──────────────────────────┘
                       │ Vue Dev Server (proxy)
          ┌────────────┴────────────┐
          │                         │
  /api/*  │                /pharma-api/*
          ▼                         ▼
┌──────────────────┐     ┌──────────────────────┐
│  app.py          │     │  pharma_app.py        │
│  Flask :5000     │     │  Flask :5001          │
│  Croma Backend   │     │  Pharma Backend       │
└────────┬─────────┘     └──────────┬────────────┘
         │                          │
         └────────────┬─────────────┘
                      ▼
             ┌─────────────────┐
             │  Redis :6379    │
             │  (shared cache) │
             └─────────────────┘
```

### Key Redis Keys

| Key | Set by | Used by |
|---|---|---|
| `croma_products` | `scraper.py` | `app.py → /products` |
| `croma_page_elements` | `scraper.py` | `app.py → /scraped-content` |
| `pharma_news` | `pharma_scraper.py` | `pharma_app.py → /news` |
| `pharma_last_updated` | `pharma_scraper.py` | `pharma_app.py → /news` |

---

## Project Structure

```
project/
├── backend/
│   ├── app.py              # Croma Flask API (port 5000)
│   ├── scraper.py          # Croma product scraper → Redis
│   ├── pharma_app.py       # Pharma Flask API (port 5001)
│   ├── pharma_scraper.py   # Pharma Google News RSS scraper → Redis
│   └── requirements.txt
└── frontend/
    ├── vue.config.js       # Dev server + proxy config
    ├── package.json
    └── src/
        ├── main.js         # App entry — mounts Vue Router
        ├── router.js       # Route: / → App.vue, /pharma → PharmaApp.vue
        ├── App.vue         # Croma Electronics UI
        ├── PharmaApp.vue   # Pharma Intelligence UI
        └── main.css        # Tailwind CSS
```

---

## Prerequisites

Make sure the following are installed before you begin:

| Requirement | Version | Notes |
|---|---|---|
| Python | 3.8+ | |
| Node.js | 14+ | |
| Redis | Any | Must be running on `localhost:6379` |
| pip | Latest | |
| npm | Latest | |

### Starting Redis

**Windows (via WSL or Docker):**
```bash
# Docker (recommended on Windows)
docker run -d -p 6379:6379 redis

# or if you have Redis installed natively
redis-server
```

**macOS:**
```bash
brew services start redis
```

**Linux:**
```bash
sudo service redis-server start
```

Verify Redis is running:
```bash
redis-cli ping
# Expected output: PONG
```

---

## Setup & Installation

### 1. Clone the Repository

```bash
git clone https://github.com/HORRIDBEAST/Croma-Scrapper.git
cd Croma-Scrapper/project
```

### 2. Backend Setup

```bash
cd backend

# Create and activate a virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

# Install all dependencies (covers both backends)
pip install -r requirements.txt
```

### 3. Frontend Setup

```bash
cd ../frontend
npm install
```

---

## Running the Application

You need **4 terminals** open simultaneously. Follow this exact order:

### Terminal 1 — Redis (if not already running as a service)
```bash
redis-server
```

---

### Terminal 2 — Croma Backend (port 5000)

```bash
cd backend
venv\Scripts\activate      # Windows
# source venv/bin/activate  # macOS/Linux

python scraper.py           # Scrape Croma & populate Redis (run once)
python app.py               # Start Flask API on :5000
```

> `scraper.py` fetches live product data from Croma and stores it in Redis under `croma_products`.  
> You only need to re-run `scraper.py` when you want fresh product data.

Expected output:
```
Successfully connected to Redis.
 * Running on http://127.0.0.1:5000
```

---

### Terminal 3 — Pharma Backend (port 5001)

```bash
cd backend
venv\Scripts\activate      # Windows
# source venv/bin/activate  # macOS/Linux

python pharma_scraper.py    # Scrape Google News RSS & populate Redis (run once)
python pharma_app.py        # Start Flask API on :5001
```

> `pharma_scraper.py` fetches the latest news articles for 13 pharma companies (Pfizer, Novartis, Sanofi, Roche, Merck, etc.) from Google News RSS and stores up to 6 articles per company in Redis. Takes ~30 seconds.

Expected output:
```
Redis connected.
Scraping news for: Pfizer
  → 6 articles found for Pfizer
...
Stored 78 articles in Redis under 'pharma_news'
 * Running on http://127.0.0.1:5001
```

---

### Terminal 4 — Vue Frontend (port 8080)

```bash
cd frontend
npm run serve
```

Expected output:
```
App running at:
  - Local:   http://localhost:8080/
```

---

## Accessing the Application

| URL | Module |
|---|---|
| http://localhost:8080/ | Croma Electronics Store |
| http://localhost:8080/pharma | Pharma Intelligence Feed |

---

## Module 1: Croma Electronics Store

**URL:** `http://localhost:8080/`

### Features
- Live product grid scraped from [Croma Televisions & Accessories](https://www.croma.com/televisions-accessories/c/997)
- Filter by category (Televisions, Audio, Streaming, Smart Home, Accessories)
- Sort by price (low→high, high→low) and name
- Search by product name or brand
- Add to Cart and Love (wishlist) counters
- Discount badge and savings display

### API Endpoints (`:5000`)

| Method | Endpoint | Description |
|---|---|---|
| GET | `/products` | Returns all scraped products from Redis |
| GET | `/scraped-content` | Returns scraped head/header HTML elements |
| GET | `/` | Health check |

---

## Module 2: Pharma Intelligence Feed

**URL:** `http://localhost:8080/pharma`

### Features
- Real-time news articles for **13 major pharma companies**
- Auto-categorised into: Drug Launch, Innovation, Events, Acquisition, Earnings, General
- Filter by company with colour-coded company badges
- Filter by news category
- Full-text search across titles and summaries
- Stats bar: total articles, companies tracked, currently showing
- **Refresh button** — triggers a live re-scrape from Google News (takes ~35 seconds)
- Direct links to original news sources

### Tracked Companies
Pfizer · Novartis · Sanofi · Takeda · Merck · Bayer · AbbVie · Bristol Myers Squibb · Johnson & Johnson · Roche · Eli Lilly · AstraZeneca · Amgen

### API Endpoints (`:5001`)

| Method | Endpoint | Query Params | Description |
|---|---|---|---|
| GET | `/news` | `company`, `category`, `search` | Returns filtered news from Redis |
| GET | `/companies` | — | Returns list of tracked companies |
| POST | `/refresh` | — | Triggers a background re-scrape |
| GET | `/` | — | Health check |

---

## Proxy Configuration

The Vue dev server proxies API requests so the frontend never hits CORS issues:

```
/api/*        →  http://127.0.0.1:5000  (Croma)
/pharma-api/* →  http://127.0.0.1:5001  (Pharma)
```

This is configured in `frontend/vue.config.js`.

---

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| Blank white screen on `localhost:8080` | Router not rendering | Ensure `main.js` uses `h(RouterView)` not `h('router-view')` |
| `HTTP 404` on Croma | `/api` proxy pointing to wrong port | Check `vue.config.js` — `/api` target must be `:5000` |
| `Proxy error` / invalid JSON on Pharma | `localhost` resolving to IPv6 | Use `127.0.0.1:5001` instead of `localhost:5001` in proxy |
| `No data found` on Pharma | Scraper not run yet | Run `python pharma_scraper.py` first |
| `Redis not connected` | Redis not running | Start Redis and verify with `redis-cli ping` |
| Pharma Refresh takes long | Expected — scraper fetches 13 companies | Wait ~35 seconds after clicking Refresh |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Vue 3, Vue Router, Tailwind CSS |
| Croma Backend | Python, Flask, Flask-CORS |
| Pharma Backend | Python, Flask, Flask-CORS, feedparser |
| Cache / Storage | Redis |
| Data Source — Croma | Croma website (Selenium/Requests scraping) |
| Data Source — Pharma | Google News RSS via feedparser |
| Dev Proxy | Vue CLI devServer proxy |
