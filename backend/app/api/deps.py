"""Shared FastAPI dependencies."""

from __future__ import annotations

from fastapi import Depends

from app.core.config import Settings, get_settings
from app.stores.memory_store import MemoryStore
from app.stores.profile_store import ProfileStore
from app.stores.reminder_store import ReminderStore
from app.stores.trace_store import TraceStore


def get_profile_store(settings: Settings = Depends(get_settings)) -> ProfileStore:
    return ProfileStore(settings.resolved_profile_dir)


def get_trace_store(settings: Settings = Depends(get_settings)) -> TraceStore:
    return TraceStore(settings.resolved_trace_log_dir)


def get_memory_store(settings: Settings = Depends(get_settings)) -> MemoryStore:
    return MemoryStore(settings.resolved_memory_root)


def get_reminder_store(settings: Settings = Depends(get_settings)) -> ReminderStore:
    return ReminderStore(settings.resolved_reminder_dir)
