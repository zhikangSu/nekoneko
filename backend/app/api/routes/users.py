"""User profile endpoints (issue #21).

    GET   /api/users/{user_id}/profile
    PATCH /api/users/{user_id}/profile

The profile holds the user-chosen ``companion_display_name`` and basic
preferences. A missing profile returns a default with ``onboarding_completed``
false so the frontend can trigger first-run naming.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_profile_store
from app.schemas.profile import ProfileUpdate, UserProfile
from app.stores.profile_store import ProfileStore

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/{user_id}/profile", response_model=UserProfile)
def get_profile(
    user_id: str,
    store: ProfileStore = Depends(get_profile_store),
) -> UserProfile:
    try:
        return store.get(user_id)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.patch("/{user_id}/profile", response_model=UserProfile)
def update_profile(
    user_id: str,
    update: ProfileUpdate,
    store: ProfileStore = Depends(get_profile_store),
) -> UserProfile:
    try:
        return store.update(user_id, update)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
