# Bookkeeping API

## Setup

```bash
cd /Users/kerriewalubengo/Desktop/bookkeeping
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Migrations

```bash
export DATABASE_URL="postgresql+psycopg2://postgres:postgres@localhost:5432/bookkeeping"
alembic upgrade head
```

## Run

```bash
uvicorn app.main:app --reload
```

## Parser Test

```bash
pip install -r requirements-dev.txt
pytest -q
```

## Seed Demo Data

```bash
python scripts/seed_dev.py
```

Uses:
- Workspace ID: 00000000-0000-0000-0000-000000000000
- Business ID: 11111111-1111-1111-1111-111111111111
```

## Seed Demo Data (API)

```bash
curl -X POST http://localhost:8000/api/seed
```

This seeds:
- Workspace `00000000-0000-0000-0000-000000000000`
- Business `11111111-1111-1111-1111-111111111111`
- Bank account `22222222-2222-2222-2222-222222222222`
