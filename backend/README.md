# Traffora Final Backend
FastAPI + SQLite + Random Forest.

Run:
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

Swagger:
http://127.0.0.1:8000/docs

Main APIs:
GET /api/health
POST /api/auth/register
POST /api/auth/login
GET /api/dashboard
GET /api/traffic
GET /api/locations
POST /api/predict
GET /api/top-congested
GET /api/trends
GET /api/incidents
POST /api/incidents
PUT /api/incidents/{id}
GET /api/predictions/history
GET /api/model/metrics
GET /api/report/location

The login token is intentionally a simple demo token for an academic prototype. Use proper JWT/password hashing for production.
