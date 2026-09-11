@echo off
cd backend
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000
pause
