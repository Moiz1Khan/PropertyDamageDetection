# OffmarketStream

AI Real Estate Investment Analyzer (FCCU FYP). Professional demo with a real FastAPI backend, deal-engine formulas, and simulated CV/ML that looks production-ready.

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

## What is real vs simulated

| Feature | Status |
|---------|--------|
| Auth (JWT) | Real |
| Property CRUD + SQLite | Real |
| Deal math (profit, ROI, max offer, rank) | Real formulas |
| PDF reports | Real (ReportLab) |
| Damage CV / ARV / rehab / rent models | Professional **simulated** pipeline (deterministic, FYP-ready) |
| Comps / neighborhood | Simulated US market data by city |

## Design doc

See `docs/AI_Real_Estate_Investment_Analyzer_Data_System_Design.pdf`
