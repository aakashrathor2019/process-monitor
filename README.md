# Process Monitor (Agent + Django Backend)

A minimal process monitoring system:
- **Agent (Python/EXE)** → collects running processes on Windows and sends snapshots to backend
- **Backend (Django + DRF + SQLite)** → stores snapshots and exposes API
- **Frontend (HTML + JS + CSS)** → displays process hierarchy in an interactive tree

## Quickstart

### Backend
```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
