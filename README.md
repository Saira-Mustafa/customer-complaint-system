# Customer Complaint System

AI-powered Customer Complaint Management System for the pharmaceutical manufacturing industry.

## Technology Stack

| Layer | Technology |
|-------|------------|
| Frontend | React (Vite) + Redux Toolkit + Tailwind CSS |
| Backend | Python + FastAPI |
| AI | LangGraph + Groq (`gemma2-9b-it`) |
| Database | PostgreSQL |
| UI Font | Google Inter |

## Project Structure

- **Frontend:** `frontend/` — React application (Vite + JavaScript)
- **Backend:** `backend/` — FastAPI application

## Getting Started

### 1. Environment variables

Copy the example env file and fill in your values (never commit real secrets):

```bash
cp .env.example .env
```

Required variables:

- `GROQ_API_KEY` — API key for Groq LLM access
- `DATABASE_URL` — PostgreSQL connection string (e.g. `postgresql+psycopg://user:password@localhost:5432/complaints`)

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

The Vite dev server typically starts at `http://localhost:5173`.

### 3. Backend

Create and activate the Python virtual environment (already named `venv` if you followed setup):

**Windows (PowerShell):**

```powershell
cd backend
.\venv\Scripts\Activate.ps1
```

**macOS / Linux:**

```bash
cd backend
source venv/bin/activate
```

Install dependencies (if needed):

```bash
pip install -r requirements.txt
```

Start the FastAPI server:

```bash
uvicorn app.main:app --reload --app-dir .
```

Or from the `backend` directory:

```bash
uvicorn app.main:app --reload
```

The API typically starts at `http://localhost:8000`. Interactive docs: `http://localhost:8000/docs`.

## Notes

This repository currently contains **project scaffolding only**. Application features (complaint UI, LangGraph agents, database models, and complaint APIs) will be added in later steps.
