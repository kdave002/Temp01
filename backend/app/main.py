from fastapi import FastAPI
from .models import DriftRequest, DriftResponse
from .drift import detect_drift, build_patch, compute_impact
from .remediation import validate_patch, build_pr_body
from .decision import recommend_action
from .config import get_settings
from .github_payload import build_pr_payload

app = FastAPI(title="DriftShield API", version="0.5.0")


@app.get("/health")
def health():
    settings = get_settings()
    return {
        "status": "ok",
        "service": "driftshield",
        "repo_configured": bool(settings.github_owner and settings.github_repo),
    }


@app.post("/analyze", response_model=DriftResponse)
def analyze(payload: DriftRequest):
    events = detect_drift(payload.previous_schema, payload.current_schema)
    impact_score, risk = compute_impact(events, payload.downstream_model_count)
    patch = build_patch(events)
    validation = validate_patch(events)
    pr_body = build_pr_body(events, impact_score, risk, patch, validation)
    action, reasons = recommend_action(risk, validation, impact_score, events)

    return DriftResponse(
        events=events,
        impact_score=impact_score,
        risk=risk,
        patch_sql=patch,
        validation=validation,
        pr_body=pr_body,
        action_recommendation=action,
        recommendation_reasons=reasons,
    )


@app.post("/pr-preview")
def pr_preview(payload: DriftRequest):
    response = analyze(payload)
    settings = get_settings()
    return build_pr_payload(response, settings)
