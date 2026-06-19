# Satellite Tracker — Python Starter

A Python-first satellite tracker using:

- **FastAPI** for the backend API
- **Tiger Cloud / Postgres** for storing satellite orbital-element snapshots
- **CelesTrak GP JSON** as the public orbital data source
- **sgp4** for orbital propagation
- A small **Three.js** browser view served from FastAPI

This starter intentionally stores **orbital elements**, not millions of precomputed positions. The backend computes current positions on demand. This keeps the first version simple, explainable, and efficient.

## Architecture

```txt
CelesTrak GP JSON
       |
       v
scripts/ingest_celestrak.py
       |
       v
Tiger Cloud / Postgres
       |
       v
FastAPI /api/positions
       |
       v
Three.js globe in browser
```

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
```

Add your Tiger Cloud connection string to `.env`:

```bash
DATABASE_URL="postgresql+psycopg://USER:PASSWORD@HOST:5432/DB?sslmode=require"
```

Create the database tables:

```bash
python scripts/init_db.py
```

Ingest a small group first:

```bash
python scripts/ingest_celestrak.py --group stations
```

Then try Starlink or active satellites:

```bash
python scripts/ingest_celestrak.py --group starlink
python scripts/ingest_celestrak.py --group active --limit 2000
```

Run the app:

```bash
uvicorn app.main:app --reload
```

Open:

```txt
http://127.0.0.1:8000
```

## API endpoints

```txt
GET /api/satellites?limit=100
GET /api/positions?limit=1000
GET /health
```

## Why this Python design works

Python is excellent for the serious parts of this project:

- data ingestion
- orbital propagation
- database work
- analytics
- scheduled jobs
- future ML/forecasting extensions

For the 3D visualization, this starter still uses a small browser-based Three.js scene, because rendering thousands of moving objects is what browsers and WebGL are best at. The project is still Python-first because Python owns the backend, data pipeline, database layer, and orbital math.


## Notes

Be polite to public data sources. Do not fetch CelesTrak every minute. For this project, refreshing every 6–12 hours is plenty.
