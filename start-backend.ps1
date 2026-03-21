# Root scripts folder: start the backend API (FastAPI + uvicorn).
Set-Location $PSScriptRoot\backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
