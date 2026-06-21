#!/usr/bin/env bash
# One-command dev: start the FastAPI backend (:8000) and the Next.js frontend
# (:3000) together; Ctrl-C stops both. Run `make setup` once first to install
# dependencies and create .env.
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [ ! -f .env ]; then
  cp .env.example .env
  echo "[dev] created .env from .env.example (DEMO_MODE=true, offline)"
fi
if [ ! -d backend/.venv ]; then
  echo "[dev] backend/.venv missing — run 'make setup' first." >&2
  exit 1
fi
if [ ! -d frontend/node_modules ]; then
  echo "[dev] frontend/node_modules missing — run 'make setup' first." >&2
  exit 1
fi

pids=()
kill_tree() {  # kill a PID and all its descendants (e.g. `next` under `npm`)
  local pid=$1 child
  for child in $(pgrep -P "$pid" 2>/dev/null); do kill_tree "$child"; done
  kill "$pid" 2>/dev/null
}
cleanup() {
  trap - INT TERM EXIT
  echo
  echo "[dev] stopping…"
  for p in "${pids[@]}"; do kill_tree "$p"; done
  wait 2>/dev/null
}
trap cleanup INT TERM EXIT

echo "[dev] backend  → http://localhost:8000"
( cd backend && . .venv/bin/activate && exec uvicorn app.main:app --reload ) &
pids+=($!)

echo "[dev] frontend → http://localhost:3000"
( cd frontend && exec npm run dev ) &
pids+=($!)

echo "[dev] both running. Open http://localhost:3000 — press Ctrl-C to stop."
wait
