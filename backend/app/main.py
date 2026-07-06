"""FastAPI application entrypoint.

Run locally:

    uvicorn app.main:app --reload
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import (
    chat,
    health,
    memory,
    memory_cards,
    reminders,
    sensors,
    traces,
    users,
    voice,
)
from app.core.config import get_settings


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="User-Named Elderly AI Companion — Backend",
        version="0.1.0",
        description="FastAPI backend for the course-demo companion AI. "
        "Runs offline in DEMO_MODE with fake/mock providers.",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router, prefix="/api")
    app.include_router(chat.router, prefix="/api")
    app.include_router(users.router, prefix="/api")
    app.include_router(traces.router, prefix="/api")
    app.include_router(memory.router, prefix="/api")
    app.include_router(memory_cards.router, prefix="/api")
    app.include_router(reminders.router, prefix="/api")
    app.include_router(sensors.router, prefix="/api")
    app.include_router(voice.router, prefix="/api")
    return app


app = create_app()
