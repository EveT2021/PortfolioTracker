# PortfolioTracker

Simple Flask + PostgreSQL portfolio tracking prototype.

Quick start (Docker Compose):

```bash
# copy .env.example -> .env and edit if needed
cp .env.example .env

docker compose up --build
```

This will start Postgres (on 5432) and the Flask API (on 5000).

Local run (without Docker for the API):

```bash
# set environment variables, then
python -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
export DATABASE_URL=postgresql://postgres:postgres@localhost/portfolio
python backend/run.py
```

API endpoints (under `/api`):

- `GET /api/health` - health check
- `GET/POST /api/assets` - list or create assets
- `GET/POST /api/transactions` - list or create transactions

Database schema reference: `db__schema.sql`
