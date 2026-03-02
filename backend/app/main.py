import logging
import secrets
import time
from collections import defaultdict, deque
from uuid import uuid4

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from .config import Settings, get_settings
from .contracts import evaluate_contract
from .decision import recommend_action
from .drift import build_patch, compute_impact, detect_drift
from .github_client import GitHubPRCreateError, GitHubPRCreateTimeout, create_pull_request
from .github_payload import build_pr_payload
from .models import (
    DriftRequest,
    DriftResponse,
    PilotReadinessRequest,
    PilotReadinessResponse,
    RoiEstimateRequest,
    RoiEstimateResponse,
    SimulationRequest,
    SimulationResponse,
)
from .remediation import build_pr_body, validate_patch

app = FastAPI(title="DriftShield API", version="0.7.0")
logger = logging.getLogger("driftshield.audit")

_RATE_LIMITED_PATHS = {
    "/analyze",
    "/simulate",
    "/roi-estimate",
    "/pilot-readiness",
    "/pr-preview",
    "/pr-create",
}
_RATE_LIMIT_STALE_FACTOR = 3
_rate_limit_buckets: dict[tuple[str, str], deque[float]] = defaultdict(deque)


def _cleanup_rate_limit_buckets(now: float, window_seconds: int) -> None:
    if not _rate_limit_buckets:
        return

    stale_before = now - (window_seconds * _RATE_LIMIT_STALE_FACTOR)
    stale_keys = [
        key
        for key, bucket in _rate_limit_buckets.items()
        if not bucket or bucket[-1] <= stale_before
    ]
    for key in stale_keys:
        _rate_limit_buckets.pop(key, None)


def _request_id_from(request: Request) -> str:
    return getattr(request.state, "request_id", "unknown")


def _client_fingerprint(request: Request) -> str:
    forwarded_for = request.headers.get("X-Forwarded-For", "").split(",")[0].strip()
    if forwarded_for:
        return forwarded_for
    if request.client and request.client.host:
        return request.client.host
    return "unknown"


def _enforce_rate_limit(request: Request, settings: Settings) -> None:
    if request.method != "POST" or request.url.path not in _RATE_LIMITED_PATHS:
        return

    max_requests = settings.rate_limit_requests
    window_seconds = settings.rate_limit_window_seconds
    if max_requests <= 0 or window_seconds <= 0:
        return

    now = time.monotonic()
    _cleanup_rate_limit_buckets(now, window_seconds)

    bucket_key = (request.url.path, _client_fingerprint(request))
    bucket = _rate_limit_buckets[bucket_key]
    window_start = now - window_seconds

    while bucket and bucket[0] <= window_start:
        bucket.popleft()

    if not bucket:
        _rate_limit_buckets.pop(bucket_key, None)
        bucket = _rate_limit_buckets[bucket_key]

    if len(bucket) >= max_requests:
        retry_after_seconds = max(1, int((bucket[0] + window_seconds) - now))
        raise HTTPException(
            status_code=429,
            detail="rate limit exceeded",
            headers={"Retry-After": str(retry_after_seconds)},
        )

    bucket.append(now)


@app.middleware("http")
async def request_correlation_and_audit_middleware(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or str(uuid4())
    request.state.request_id = request_id

    settings = get_settings()

    status_code = 500
    try:
        _enforce_rate_limit(request, settings)
        response = await call_next(request)
        status_code = response.status_code
    except HTTPException as exc:
        status_code = exc.status_code
        response_headers = {"X-Request-ID": request_id}
        if exc.headers:
            response_headers.update(exc.headers)
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail, "request_id": request_id},
            headers=response_headers,
        )
    except Exception:
        raise
    else:
        response.headers["X-Request-ID"] = request_id
        return response
    finally:
        logger.info(
            "method=%s path=%s status=%s request_id=%s",
            request.method,
            request.url.path,
            status_code,
            request_id,
        )


@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exc: RequestValidationError):
    request_id = _request_id_from(request)
    return JSONResponse(
        status_code=422,
        content={
            "detail": "invalid request payload",
            "errors": jsonable_encoder(exc.errors()),
            "request_id": request_id,
        },
        headers={"X-Request-ID": request_id},
    )


@app.exception_handler(HTTPException)
def http_exception_handler(request: Request, exc: HTTPException):
    request_id = _request_id_from(request)
    detail = exc.detail
    if isinstance(detail, dict):
        detail = {**detail, "request_id": request_id}
    response_headers = {"X-Request-ID": request_id}
    if exc.headers:
        response_headers.update(exc.headers)
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": detail, "request_id": request_id},
        headers=response_headers,
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


def _require_pr_create_api_key(settings: Settings, provided_key: str | None) -> None:
    configured_key = settings.driftshield_api_key
    if not configured_key:
        return

    if not provided_key or not secrets.compare_digest(provided_key, configured_key):
        raise HTTPException(status_code=401, detail="unauthorized")


def _validate_simulation_request(payload: SimulationRequest) -> None:
    total_columns = len(payload.previous_schema) + len(payload.current_schema)
    if total_columns == 0:
        raise HTTPException(status_code=422, detail="schema input cannot be empty")
    if total_columns > 600:
        raise HTTPException(status_code=422, detail="schema input too large for simulation endpoint")
    if payload.downstream_model_count > 5000:
        raise HTTPException(status_code=422, detail="downstream_model_count too high for simulation endpoint")


def _round2(value: float) -> float:
    return round(value, 2)


def _estimate_roi(payload: RoiEstimateRequest) -> RoiEstimateResponse:
    adoption = payload.driftshield_adoption_rate

    incident_reduction_rate = 0.20 * adoption
    mttd_reduction_rate = 0.35 * adoption
    mttr_reduction_rate = 0.40 * adoption

    baseline_hours_per_incident = payload.mean_time_to_detect_hours + payload.mean_time_to_resolve_hours
    baseline_monthly_engineering_hours = (
        payload.incidents_per_month
        * baseline_hours_per_incident
        * payload.engineers_involved_per_incident
    )

    projected_incidents_per_month = payload.incidents_per_month * (1 - incident_reduction_rate)
    projected_mttd_hours = payload.mean_time_to_detect_hours * (1 - mttd_reduction_rate)
    projected_mttr_hours = payload.mean_time_to_resolve_hours * (1 - mttr_reduction_rate)

    projected_hours_per_incident = projected_mttd_hours + projected_mttr_hours
    projected_monthly_engineering_hours = (
        projected_incidents_per_month
        * projected_hours_per_incident
        * payload.engineers_involved_per_incident
    )

    baseline_monthly_cost_usd = baseline_monthly_engineering_hours * payload.hourly_engineering_cost_usd
    projected_monthly_cost_usd = projected_monthly_engineering_hours * payload.hourly_engineering_cost_usd

    monthly_engineering_hours_saved = max(0.0, baseline_monthly_engineering_hours - projected_monthly_engineering_hours)
    monthly_incidents_prevented = max(0.0, payload.incidents_per_month - projected_incidents_per_month)
    monthly_cost_saved_usd = max(0.0, baseline_monthly_cost_usd - projected_monthly_cost_usd)

    monthly_cost_savings_percent = (
        (monthly_cost_saved_usd / baseline_monthly_cost_usd) * 100.0 if baseline_monthly_cost_usd > 0 else 0.0
    )

    return RoiEstimateResponse(
        baseline_monthly_engineering_hours=_round2(baseline_monthly_engineering_hours),
        baseline_monthly_cost_usd=_round2(baseline_monthly_cost_usd),
        projected_monthly_engineering_hours=_round2(projected_monthly_engineering_hours),
        projected_monthly_cost_usd=_round2(projected_monthly_cost_usd),
        monthly_engineering_hours_saved=_round2(monthly_engineering_hours_saved),
        annual_engineering_hours_saved=_round2(monthly_engineering_hours_saved * 12),
        monthly_incidents_prevented=_round2(monthly_incidents_prevented),
        monthly_cost_saved_usd=_round2(monthly_cost_saved_usd),
        annual_cost_saved_usd=_round2(monthly_cost_saved_usd * 12),
        monthly_cost_savings_percent=_round2(monthly_cost_savings_percent),
        assumptions={
            "adoption_rate": adoption,
            "incident_reduction_rate": incident_reduction_rate,
            "mttd_reduction_rate": mttd_reduction_rate,
            "mttr_reduction_rate": mttr_reduction_rate,
        },
    )


def _pilot_readiness(payload: PilotReadinessRequest) -> PilotReadinessResponse:
    checks = {
        "data_owner_identified": payload.data_owner_identified,
        "repo_access_configured": payload.repo_access_configured,
        "ci_green": payload.ci_green,
        "rollback_plan_defined": payload.rollback_plan_defined,
        "oncall_contact_set": payload.oncall_contact_set,
    }

    passed = [name for name, ok in checks.items() if ok]
    missing = [name for name, ok in checks.items() if not ok]
    score = int(round((len(passed) / len(checks)) * 100))

    if score == 100:
        status = "ready"
        recommendation = "Pilot can start immediately with standard change windows."
    elif score >= 60:
        status = "ready_with_risks"
        recommendation = "Pilot can start, but close missing readiness items before enabling auto PR create."
    else:
        status = "not_ready"
        recommendation = "Do not start pilot yet; complete core operational readiness items first."

    return PilotReadinessResponse(
        readiness_score=score,
        status=status,
        missing_items=missing,
        recommendation=recommendation,
    )


def _simulate(payload: SimulationRequest) -> SimulationResponse:
    events = detect_drift(payload.previous_schema, payload.current_schema)
    impact_score, risk = compute_impact(events, payload.downstream_model_count)
    validation = validate_patch(events)
    action, _ = recommend_action(risk, validation, impact_score, events)
    compatibility = evaluate_contract(payload.previous_schema, payload.current_schema)

    if compatibility.compatible and risk == "low":
        breakage_class = "non_breaking"
    elif risk == "high" or not compatibility.compatible:
        breakage_class = "likely_breaking"
    else:
        breakage_class = "potentially_breaking"

    path_map = {
        "auto_merge_candidate": "auto patch + lightweight review",
        "open_pr_and_request_review": "open PR + data-owner review",
        "manual_approval_required": "manual approval + staged rollout",
    }
    repair_path = path_map.get(action, "open PR + manual review")

    mean_event_conf = (
        sum(e.confidence for e in events if e.confidence is not None)
        / max(1, len([e for e in events if e.confidence is not None]))
        if any(e.confidence is not None for e in events)
        else (0.9 if not events else 0.6)
    )

    baseline_bonus = 0.0
    if payload.metric_baselines:
        supplied = [
            payload.metric_baselines.incidents_per_month,
            payload.metric_baselines.mean_time_to_detect_hours,
            payload.metric_baselines.mean_time_to_resolve_hours,
        ]
        baseline_bonus = 0.1 * (sum(v is not None for v in supplied) / 3.0)

    confidence = max(
        0.2,
        min(
            0.95,
            0.45 + (0.35 * mean_event_conf) + (0.05 if compatibility.compatible else -0.05) - (impact_score / 400) + baseline_bonus,
        ),
    )

    if confidence >= 0.75:
        band = "high"
        band_range = {"min": 0.75, "max": 0.95}
    elif confidence >= 0.45:
        band = "medium"
        band_range = {"min": 0.45, "max": 0.74}
    else:
        band = "low"
        band_range = {"min": 0.2, "max": 0.44}

    summary = (
        f"{len(events)} drift event(s), impact {impact_score}/100 ({risk}), "
        f"contract={'compatible' if compatibility.compatible else 'breaking'}"
    )

    return SimulationResponse(
        predicted_breakage_class=breakage_class,
        expected_repair_path=repair_path,
        confidence_score=round(confidence, 3),
        confidence_band=band,
        confidence_range=band_range,
        summary=summary,
    )


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


@app.post("/roi-estimate", response_model=RoiEstimateResponse)
def roi_estimate(payload: RoiEstimateRequest):
    return _estimate_roi(payload)


@app.post("/simulate", response_model=SimulationResponse)
def simulate(payload: SimulationRequest):
    _validate_simulation_request(payload)
    return _simulate(payload)


@app.post("/pilot-readiness", response_model=PilotReadinessResponse)
def pilot_readiness(payload: PilotReadinessRequest):
    return _pilot_readiness(payload)


@app.post("/pr-preview")
def pr_preview(payload: DriftRequest):
    settings = get_settings()
    _validate_pr_endpoint_request(payload, settings)
    response = _run_analysis(payload)
    return build_pr_payload(response, settings)


@app.post("/pr-create")
def pr_create(
    payload: DriftRequest,
    x_driftshield_key: str | None = Header(default=None, alias="X-DriftShield-Key"),
):
    settings = get_settings()
    _validate_pr_endpoint_request(payload, settings)
    _require_pr_create_api_key(settings, x_driftshield_key)

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
