"""Shared FastAPI dependencies."""

from __future__ import annotations

from fastapi import Depends

from app.core.config import Settings, get_settings
from app.stores.profile_store import ProfileStore


def get_profile_store(settings: Settings = Depends(get_settings)) -> ProfileStore:
    return ProfileStore(settings.profile_dir)
