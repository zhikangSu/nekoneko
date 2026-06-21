# One-command dev for the User-Named Elderly AI Companion demo.
# See README.md → Quick start. Everything defaults to DEMO_MODE (offline).
.PHONY: help setup dev backend frontend test clean

help:
	@echo "make setup     install backend + frontend deps and create .env"
	@echo "make dev       run backend (:8000) + frontend (:3000) together (Ctrl-C stops both)"
	@echo "make backend   run only the FastAPI backend"
	@echo "make frontend  run only the Next.js frontend"
	@echo "make test      backend pytest + frontend build"

setup:
	cd backend && python3 -m venv .venv && . .venv/bin/activate && pip install -e ".[dev]"
	cd frontend && npm install
	[ -f .env ] || cp .env.example .env
	@echo "Setup done. Run 'make dev'."

dev:
	bash scripts/dev.sh

backend:
	cd backend && . .venv/bin/activate && uvicorn app.main:app --reload

frontend:
	cd frontend && npm run dev

test:
	cd backend && . .venv/bin/activate && pytest
	cd frontend && npm run build
