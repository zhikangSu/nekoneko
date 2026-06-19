"""Shared FastAPI dependencies."""

from __future__ import annotations

from fastapi import Depends

from app.core.config import Settings, get_settings
from app.stores.profile_store import ProfileStore
from app.stores.trace_store import TraceStore


def get_profile_store(settings: Settings = Depends(get_settings)) -> ProfileStore:
    return ProfileStore(settings.resolved_profile_dir)


def get_trace_store(settings: Settings = Depends(get_settings)) -> TraceStore:
    return TraceStore(settings.resolved_trace_log_dir)
