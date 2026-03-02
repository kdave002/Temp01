PYTHON ?= python3
VENV ?= .venv
PIP := $(VENV)/bin/pip
PYTEST := $(VENV)/bin/pytest
UVICORN := $(VENV)/bin/uvicorn

.PHONY: setup test lint check smoke run

setup:
	$(PYTHON) -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r backend/requirements.txt

test:
	$(PYTEST) -q

lint:
	$(PYTHON) -m compileall -q backend tests

check: lint test

smoke:
	$(VENV)/bin/python scripts/smoke.py

run:
	$(UVICORN) backend.app.main:app --reload
