#!/usr/bin/env python3
"""Local smoke test for DriftShield API.

Runs a lightweight end-to-end check against a locally started app:
1) GET /health
2) POST /analyze with a small sample payload
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request

HOST = os.environ.get("SMOKE_HOST", "127.0.0.1")
PORT = int(os.environ.get("SMOKE_PORT", "8001"))
BASE_URL = f"http://{HOST}:{PORT}"


class SmokeError(RuntimeError):
    pass


def _request(method: str, path: str, payload: dict | None = None, timeout: float = 5.0) -> tuple[int, dict]:
    data = None
    headers = {"Content-Type": "application/json"}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(f"{BASE_URL}{path}", data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8")
            parsed = json.loads(body) if body else {}
            return resp.status, parsed
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8")
        parsed = json.loads(body) if body else {}
        return exc.code, parsed


def _wait_for_health(max_wait_seconds: float = 15.0) -> None:
    deadline = time.time() + max_wait_seconds
    while time.time() < deadline:
        try:
            status, body = _request("GET", "/health", payload=None, timeout=2.0)
            if status == 200 and body.get("status") == "ok":
                return
        except Exception:
            pass
        time.sleep(0.5)
    raise SmokeError("service did not become healthy in time")


def _assert_health() -> None:
    status, body = _request("GET", "/health")
    if status != 200:
        raise SmokeError(f"/health returned HTTP {status}: {body}")
    if body.get("status") != "ok":
        raise SmokeError(f"/health status mismatch: {body}")


def _assert_analyze() -> None:
    sample = {
        "previous_schema": [
            {"name": "customer_id", "type": "int"},
            {"name": "email", "type": "string"},
        ],
        "current_schema": [
            {"name": "customer_id", "type": "int"},
            {"name": "email_address", "type": "string"},
            {"name": "country", "type": "string"},
        ],
        "downstream_model_count": 3,
    }
    status, body = _request("POST", "/analyze", payload=sample)
    if status != 200:
        raise SmokeError(f"/analyze returned HTTP {status}: {body}")

    required_keys = {"events", "impact_score", "risk", "patch_sql", "validation", "pr_body", "action_recommendation"}
    missing = sorted(required_keys - set(body.keys()))
    if missing:
        raise SmokeError(f"/analyze missing keys: {missing}")


def main() -> int:
    cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        "backend.app.main:app",
        "--host",
        HOST,
        "--port",
        str(PORT),
    ]

    proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        _wait_for_health()
        _assert_health()
        _assert_analyze()
        print("SMOKE_OK")
        return 0
    except Exception as exc:
        print(f"SMOKE_FAIL: {exc}", file=sys.stderr)
        return 1
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()


if __name__ == "__main__":
    raise SystemExit(main())
