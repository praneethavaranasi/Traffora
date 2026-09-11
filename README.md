# TRAFFORA — COMPLETE FINAL PROJECT

Traffic Prediction for Intelligent Transportation System using Machine Learning.

## What is included

### Frontend

- Professional Streamlit dashboard
- AI prediction interface
- Live traffic table
- Route Advisor
- Incident management
- Reports and CSV export
- Model performance
- Prediction history

### Backend

- FastAPI REST API
- Random Forest prediction
- Dashboard analytics
- Traffic/location/trend APIs
- Incident CRUD
- Authentication demo
- SQLite database
- Prediction history

### ML

- 40,000-record Hyderabad-style dataset
- Existing trained Random Forest pipeline
- Low / Medium / High congestion

## Run

### Terminal 1

```bash
cd backend
pip install -r requirements.txt
Backend python command: python -m uvicorn main:app --reload --port 8000
```

### Terminal 2

```bash
cd frontend
pip install -r requirements.txt
streamlit run app.py
command in terminal 2: python -m streamlit run app.py
```

Open the Streamlit URL shown in the terminal.

Swagger:
http://127.0.0.1:8000/docs

## Project presentation flow

Input traffic conditions
→ Frontend
→ FastAPI
→ Random Forest
→ Prediction + confidence
→ Dashboard

## Important academic note

The supplied 40,000-record dataset is synthetic/augmented Hyderabad-style data. State this honestly in the report. For a production system, replace or augment it with official sensor/GPS/traffic-camera/weather data.

## Security note

Authentication in this student prototype is intentionally simple. For production, use HTTPS, JWT access tokens, secure password hashing such as bcrypt/Argon2, restricted CORS, validation, and a production database.

## Frontend reference UI

The frontend dashboard is redesigned to closely follow the supplied Traffora reference: dark navy control-room layout, sidebar, KPI cards, Hyderabad traffic map, AI prediction panel, trend chart, congestion donut, incidents, and top congested roads.
