from fastapi import FastAPI
from .models import DriftRequest, DriftResponse
from .drift import detect_drift, build_patch

app = FastAPI(title="DriftShield API", version="0.1.0")


@app.get("/health")
def health():
    return {"status": "ok", "service": "driftshield"}


@app.post("/analyze", response_model=DriftResponse)
def analyze(payload: DriftRequest):
    events = detect_drift(payload.previous_schema, payload.current_schema)
    patch = build_patch(events)
    return DriftResponse(events=events, patch_sql=patch)
