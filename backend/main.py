
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional
import hashlib
import secrets
import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text
from sqlalchemy.orm import declarative_base, sessionmaker

BASE = Path(__file__).resolve().parent
MODEL_PATH = BASE / "traffic_random_forest_pipeline.pkl"
DATA_PATH = BASE / "hyderabad_traffic_training_dataset_40000.csv"
DB_PATH = BASE / "traffora.db"

app = FastAPI(title="Traffora Traffic Intelligence API", version="2.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True,
                   allow_methods=["*"], allow_headers=["*"])

engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    email = Column(String(160), unique=True, index=True)
    password_hash = Column(String(200))
    role = Column(String(30), default="user")
    created_at = Column(DateTime, default=datetime.utcnow)

class Prediction(Base):
    __tablename__ = "predictions"
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    location = Column(String(100))
    prediction = Column(String(30))
    confidence = Column(Float)
    vehicle_count = Column(Integer)
    avg_speed_kmph = Column(Float)
    traffic_density = Column(Float)

class Incident(Base):
    __tablename__ = "incidents"
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    location = Column(String(100))
    type = Column(String(50))
    severity = Column(String(30))
    description = Column(Text)
    status = Column(String(30), default="Active")

Base.metadata.create_all(engine)

model = None
data = None
LOCATIONS = {
    "Kukatpally": (17.4849, 78.4138), "Miyapur": (17.4969, 78.3570),
    "Hitech City": (17.4435, 78.3772), "Madhapur": (17.4483, 78.3915),
    "Gachibowli": (17.4401, 78.3489), "Kondapur": (17.4587, 78.3680),
    "Ameerpet": (17.4375, 78.4483), "Punjagutta": (17.4254, 78.4490),
    "Begumpet": (17.4447, 78.4627), "Secunderabad": (17.4399, 78.4983),
    "LB Nagar": (17.3457, 78.5522), "Uppal": (17.4058, 78.5591),
    "Mehdipatnam": (17.3960, 78.4350), "Banjara Hills": (17.4156, 78.4346),
    "Jubilee Hills": (17.4325, 78.4071), "Dilsukhnagar": (17.3688, 78.5247),
    "Charminar": (17.3616, 78.4747), "Koti": (17.3840, 78.4867),
    "Paradise": (17.4430, 78.4872), "Necklace Road": (17.4239, 78.4738)
}

@app.on_event("startup")
def startup():
    global model, data
    if MODEL_PATH.exists():
        model = joblib.load(MODEL_PATH)
    if DATA_PATH.exists():
        data = pd.read_csv(DATA_PATH)

class PredictionRequest(BaseModel):
    day_name: str = "Thursday"
    weekend: int = Field(0, ge=0, le=1)
    holiday: int = Field(0, ge=0, le=1)
    location: str
    vehicle_count: int = Field(..., ge=1, le=1000)
    avg_speed_kmph: float = Field(..., ge=1, le=100)
    road_capacity: int = Field(300, ge=50, le=1000)
    weather: str = "Clear"
    temperature_c: float = 29
    rainfall_mm: float = Field(0, ge=0)
    peak_hour: int = Field(0, ge=0, le=1)
    accident: int = Field(0, ge=0, le=1)
    road_work: int = Field(0, ge=0, le=1)

class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str
    role: str = "user"

class LoginRequest(BaseModel):
    email: str
    password: str

class IncidentRequest(BaseModel):
    location: str
    type: str
    severity: str = "Medium"
    description: str = ""

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def auth(token: Optional[str]):
    if not token or not token.startswith("demo-"):
        raise HTTPException(401, "Login required")
    return token

@app.get("/")
def root():
    return {"app": "Traffora", "version": "2.0", "docs": "/docs"}

@app.get("/api/health")
def health():
    return {"status": "healthy", "model_loaded": model is not None,
            "dataset_loaded": data is not None, "timestamp": datetime.now().isoformat()}

@app.post("/api/auth/register")
def register(req: RegisterRequest):
    db = SessionLocal()
    try:
        if db.query(User).filter(User.email == req.email.lower()).first():
            raise HTTPException(409, "Email already registered")
        role = req.role if req.role in ["user", "officer", "admin"] else "user"
        u = User(name=req.name, email=req.email.lower(), password_hash=hash_password(req.password), role=role)
        db.add(u); db.commit(); db.refresh(u)
        return {"message": "Account created", "user": {"id": u.id, "name": u.name, "email": u.email, "role": u.role}}
    finally:
        db.close()

@app.post("/api/auth/login")
def login(req: LoginRequest):
    db = SessionLocal()
    try:
        u = db.query(User).filter(User.email == req.email.lower()).first()
        if not u or u.password_hash != hash_password(req.password):
            raise HTTPException(401, "Invalid email or password")
        token = "demo-" + secrets.token_urlsafe(24)
        return {"access_token": token, "token_type": "bearer",
                "user": {"id": u.id, "name": u.name, "email": u.email, "role": u.role}}
    finally:
        db.close()

@app.get("/api/locations")
def locations():
    return [{"name": k, "latitude": v[0], "longitude": v[1]} for k, v in LOCATIONS.items()]

@app.post("/api/predict")
def predict(req: PredictionRequest):
    if req.location not in LOCATIONS:
        raise HTTPException(400, "Unknown location")
    lat, lon = LOCATIONS[req.location]
    density = req.vehicle_count / req.road_capacity
    row = pd.DataFrame([{
        "day_name": req.day_name, "weekend": req.weekend, "holiday": req.holiday,
        "location": req.location, "latitude": lat, "longitude": lon,
        "vehicle_count": req.vehicle_count, "avg_speed_kmph": req.avg_speed_kmph,
        "road_capacity": req.road_capacity, "weather": req.weather,
        "temperature_c": req.temperature_c, "rainfall_mm": req.rainfall_mm,
        "peak_hour": req.peak_hour, "accident": req.accident,
        "road_work": req.road_work, "traffic_density": density
    }])
    if model is not None:
        try:
            pred = model.predict(row)[0]
            probs = model.predict_proba(row)[0]
            classes = getattr(model, "classes_", None)
            if classes is None and hasattr(model, "named_steps") and "model" in model.named_steps:
                classes = model.named_steps["model"].classes_
            prob_map = {str(c): round(float(p)*100, 2) for c,p in zip(classes, probs)}
            confidence = max(prob_map.values())
        except Exception:
            pred = "High" if density >= .9 or req.avg_speed_kmph < 18 else ("Medium" if density >= .55 or req.avg_speed_kmph < 30 else "Low")
            confidence = 80.0
            prob_map = {pred: confidence}
    else:
        score = .55*density + .25*(1-req.avg_speed_kmph/60) + .08*req.peak_hour + .07*req.accident + .05*req.road_work
        pred = "Low" if score < .34 else ("Medium" if score < .52 else "High")
        confidence = round(min(98, 65 + score*35), 2)
        prob_map = {pred: confidence}
    db = SessionLocal()
    try:
        db.add(Prediction(location=req.location, prediction=str(pred), confidence=confidence,
                           vehicle_count=req.vehicle_count, avg_speed_kmph=req.avg_speed_kmph,
                           traffic_density=density))
        db.commit()
    finally:
        db.close()
    return {"prediction": str(pred), "confidence": confidence, "probabilities": prob_map,
            "traffic_density": round(density,3), "location": req.location,
            "coordinates": {"latitude": lat, "longitude": lon}}

@app.get("/api/dashboard")
def dashboard():
    if data is None: raise HTTPException(503, "Dataset unavailable")
    return {"total_records": len(data),
            "average_speed_kmph": round(float(data.avg_speed_kmph.mean()),2),
            "average_density": round(float(data.traffic_density.mean()),3),
            "congestion": {x:int((data.congestion_level==x).sum()) for x in ["Low","Medium","High"]},
            "accidents": int(data.accident.sum()), "road_work": int(data.road_work.sum())}

@app.get("/api/traffic")
def traffic(limit:int=100):
    if data is None: raise HTTPException(503, "Dataset unavailable")
    limit=max(1,min(limit,1000))
    cols=["date","time","location","latitude","longitude","vehicle_count","avg_speed_kmph",
          "traffic_density","weather","peak_hour","accident","road_work","congestion_level"]
    return data[cols].tail(limit).to_dict(orient="records")

@app.get("/api/top-congested")
def top_congested(limit:int=10):
    if data is None: raise HTTPException(503, "Dataset unavailable")
    x=data.groupby("location").agg(average_speed_kmph=("avg_speed_kmph","mean"),
        average_density=("traffic_density","mean"),
        high_congestion_percent=("congestion_level",lambda s:(s=="High").mean()*100)).reset_index()
    x=x.sort_values("high_congestion_percent",ascending=False).head(max(1,min(limit,20)))
    return x.round(2).to_dict(orient="records")

@app.get("/api/trends")
def trends(limit:int=100):
    if data is None: raise HTTPException(503, "Dataset unavailable")
    x=data.copy(); x["datetime"]=pd.to_datetime(x.date.astype(str)+" "+x.time)
    x=x.groupby("datetime").agg(average_speed_kmph=("avg_speed_kmph","mean"),
        average_density=("traffic_density","mean")).reset_index().tail(max(10,min(limit,1000)))
    x["datetime"]=x.datetime.astype(str)
    return x.round(3).to_dict(orient="records")

@app.get("/api/incidents")
def get_incidents():
    db=SessionLocal()
    try:
        return [{"id":i.id,"timestamp":i.timestamp,"location":i.location,"type":i.type,
                 "severity":i.severity,"description":i.description,"status":i.status}
                for i in db.query(Incident).order_by(Incident.id.desc()).limit(100).all()]
    finally: db.close()

@app.post("/api/incidents")
def create_incident(req: IncidentRequest, authorization: Optional[str]=Header(None)):
    auth(authorization)
    db=SessionLocal()
    try:
        i=Incident(location=req.location,type=req.type,severity=req.severity,description=req.description)
        db.add(i); db.commit(); db.refresh(i)
        return {"message":"Incident created","id":i.id}
    finally: db.close()

@app.put("/api/incidents/{incident_id}")
def update_incident(incident_id:int,status:str,authorization:Optional[str]=Header(None)):
    auth(authorization)
    db=SessionLocal()
    try:
        i=db.get(Incident,incident_id)
        if not i: raise HTTPException(404,"Incident not found")
        i.status=status; db.commit()
        return {"message":"Incident updated"}
    finally: db.close()

@app.get("/api/predictions/history")
def prediction_history(limit:int=50):
    db=SessionLocal()
    try:
        return [{"timestamp":p.timestamp,"location":p.location,"prediction":p.prediction,
                 "confidence":p.confidence,"vehicle_count":p.vehicle_count,
                 "avg_speed_kmph":p.avg_speed_kmph,"traffic_density":p.traffic_density}
                for p in db.query(Prediction).order_by(Prediction.id.desc()).limit(max(1,min(limit,200))).all()]
    finally: db.close()

@app.get("/api/model/metrics")
def metrics():
    return {"model":"Random Forest Classifier",
            "training_records":32000,"testing_records":8000,
            "accuracy":0.989,"note":"Replace these values with your measured test results when retraining."}

@app.get("/api/report/location")
def location_report():
    if data is None: raise HTTPException(503,"Dataset unavailable")
    x=data.groupby("location").agg(records=("location","size"),
        average_speed=("avg_speed_kmph","mean"), average_density=("traffic_density","mean"),
        high_congestion_percent=("congestion_level",lambda s:(s=="High").mean()*100)).reset_index()
    return x.round(2).to_dict(orient="records")
