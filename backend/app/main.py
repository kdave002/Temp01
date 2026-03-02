from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from .config import Settings, get_settings
from .contracts import evaluate_contract
from .decision import recommend_action
from .drift import build_patch, compute_impact, detect_drift
from .github_client import GitHubPRCreateError, GitHubPRCreateTimeout, create_pull_request
from .github_payload import build_pr_payload
from .models import DriftRequest, DriftResponse
from .remediation import build_pr_body, validate_patch

app = FastAPI(title="DriftShield API", version="0.6.0")


@app.exception_handler(RequestValidationError)
def validation_exception_handler(_request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": "invalid request payload", "errors": exc.errors()},
    )


def _run_analysis(payload: DriftRequest) -> DriftResponse:
    events = detect_drift(payload.previous_schema, payload.current_schema)
    impact_score, risk = compute_impact(events, payload.downstream_model_count)
    patch = build_patch(events)
    validation = validate_patch(events)
    pr_body = build_pr_body(events, impact_score, risk, patch, validation)
    action, reasons = recommend_action(risk, validation, impact_score, events)

    compatibility = evaluate_contract(payload.previous_schema, payload.current_schema)
    if not compatibility.compatible:
        reasons = reasons + ["contract_breaking=" + ",".join(compatibility.breaking_reasons)]

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


def _validate_pr_endpoint_request(payload: DriftRequest, settings: Settings) -> None:
    if not (settings.github_owner and settings.github_repo):
        raise HTTPException(status_code=503, detail="PR integration is not configured")

    total_columns = len(payload.previous_schema) + len(payload.current_schema)
    if total_columns == 0:
        raise HTTPException(status_code=422, detail="schema input cannot be empty")
    if total_columns > 600:
        raise HTTPException(status_code=422, detail="schema input too large for PR endpoints")
    if payload.downstream_model_count > 5000:
        raise HTTPException(status_code=422, detail="downstream_model_count too high for PR endpoints")


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
    return _run_analysis(payload)


@app.post("/pr-preview")
def pr_preview(payload: DriftRequest):
    settings = get_settings()
    _validate_pr_endpoint_request(payload, settings)
    response = _run_analysis(payload)
    return build_pr_payload(response, settings)


@app.post("/pr-create")
def pr_create(payload: DriftRequest):
    settings = get_settings()
    _validate_pr_endpoint_request(payload, settings)

    analysis = _run_analysis(payload)
    pr_payload = build_pr_payload(analysis, settings)

    if not settings.github_token:
        return {
            "status": "dry_run",
            "dry_run": True,
            "reason": "missing_github_configuration",
            "missing": ["GITHUB_TOKEN"],
            "pr_payload": pr_payload,
        }

    try:
        created = create_pull_request(pr_payload, settings)
        return {
            "status": "created",
            "dry_run": False,
            "pull_request_url": created.get("html_url"),
            "pull_request_number": created.get("number"),
            "github_response": created,
        }
    except GitHubPRCreateTimeout as exc:
        raise HTTPException(status_code=504, detail="GitHub API request timed out") from exc
    except GitHubPRCreateError as exc:
        raise HTTPException(status_code=502, detail="GitHub PR creation failed") from exc
