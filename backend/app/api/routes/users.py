"""User profile endpoints (issue #21).

    GET   /api/users/{user_id}/profile
    PATCH /api/users/{user_id}/profile

The profile holds the user-chosen ``companion_display_name`` and basic
preferences. A missing profile returns a default with ``onboarding_completed``
false so the frontend can trigger first-run naming.

Proactive limit fields are optional per-user overrides. Responses also expose
the resolved values that GuardianAgent actually applies.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_profile_store
from app.core.config import Settings, get_settings
from app.schemas.profile import ProfileUpdate, UserProfile, UserProfileResponse
from app.services.proactive_preferences import resolve_proactive_effective
from app.stores.profile_store import ProfileStore

router = APIRouter(prefix="/users", tags=["users"])


def _with_effective(
    profile: UserProfile,
    settings: Settings,
) -> UserProfileResponse:
    return UserProfileResponse(
        **profile.model_dump(),
        proactive_effective=resolve_proactive_effective(profile, settings),
    )


@router.get("/{user_id}/profile", response_model=UserProfileResponse)
def get_profile(
    user_id: str,
    store: ProfileStore = Depends(get_profile_store),
    settings: Settings = Depends(get_settings),
) -> UserProfileResponse:
    try:
        return _with_effective(store.get(user_id), settings)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.patch("/{user_id}/profile", response_model=UserProfileResponse)
def update_profile(
    user_id: str,
    update: ProfileUpdate,
    store: ProfileStore = Depends(get_profile_store),
    settings: Settings = Depends(get_settings),
) -> UserProfileResponse:
    try:
        return _with_effective(store.update(user_id, update), settings)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
