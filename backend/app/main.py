from fastapi import FastAPI
from .models import DriftRequest, DriftResponse
from .drift import detect_drift, build_patch, compute_impact
from .remediation import validate_patch, build_pr_body

app = FastAPI(title="DriftShield API", version="0.3.0")


@app.get("/health")
def health():
    return {"status": "ok", "service": "driftshield"}


@app.post("/analyze", response_model=DriftResponse)
def analyze(payload: DriftRequest):
    events = detect_drift(payload.previous_schema, payload.current_schema)
    impact_score, risk = compute_impact(events, payload.downstream_model_count)
    patch = build_patch(events)
    validation = validate_patch(events)
    pr_body = build_pr_body(events, impact_score, risk, patch, validation)
    return DriftResponse(
        events=events,
        impact_score=impact_score,
        risk=risk,
        patch_sql=patch,
        validation=validation,
        pr_body=pr_body,
    )
