# OffmarketStream

AI Real Estate Investment Analyzer (FCCU FYP). FastAPI backend, YOLOv8 + Gemini photo inspection, and transparent deal-engine formulas.

## Stack

- **Frontend:** React + Vite + TypeScript + Tailwind (`frontend/`)
- **Backend:** FastAPI + SQLite + JWT (`backend/`)
- **Deployed UI:** https://prop-iq-eight.vercel.app  
  (API runs locally for full analysis; Vercel hosts the frontend)

## Quick start

### 1. Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

API docs: http://127.0.0.1:8000/docs

### 2. Frontend

```powershell
cd frontend
npm install
npm run dev
```

App: http://127.0.0.1:5173

## Demo logins

| Role | Email | Password |
|------|-------|----------|
| Investor | demo@offmarketstream.com | demo123 |
| Agent | agent@offmarketstream.com | agent123 |
| Admin | admin@offmarketstream.com | admin123 |

## How the analysis works

| Step | Source |
|------|--------|
| Auth (JWT), property CRUD, PDF reports | Real |
| Damage detection | **YOLOv8n** (our trained model, `backend/models/damage_yolov8n/best.pt`) + **Gemini vision** per photo: room type, visible damage, severity, area, and a check of every YOLO box |
| Room of each photo | Set by the user, otherwise AI (only when confident), otherwise "Room not specified" |
| Rehab cost | Itemised from detected damage (unit cost × area × severity) + cosmetic refresh + 10% contingency |
| ARV | Current value (RentCast AVM → comps → regional table → list price, each sanity-checked against the list price) + value restored by repairs |
| Rent, comps, ZIP market stats | RentCast when configured; otherwise labelled estimates |
| Deal metrics, strategy, rank | Formulas in `backend/app/services/deal_engine.py` |

Nothing is randomly generated. Every number records where it came from (`valuation` on each property) and the UI shows it.

### Environment (`backend/.env` locally, `deploy/.env.production` on the server)

```
GEMINI_API_KEY=...        # free key from aistudio.google.com (optional; without it YOLO runs alone)
RENTCAST_API_KEY=...      # optional; comps/AVM/rent/market stats
SECRET_KEY=...            # JWT signing key — set a long random value in production
```

`GET /api/health` shows whether the damage model, AI vision and market data are active.

## Design doc

See `docs/AI_Real_Estate_Investment_Analyzer_Data_System_Design.pdf`
