"""Reminder endpoints (issue #11, docs/05 §6.3).

    GET    /api/reminders/{user_id}
    POST   /api/reminders/{user_id}
    DELETE /api/reminders/{user_id}/{reminder_id}
    POST   /api/reminders/{user_id}/{reminder_id}/confirm
    POST   /api/reminders/{user_id}/{reminder_id}/trigger   (manual demo fire)
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_reminder_store
from app.schemas.reminder import Reminder, ReminderCreate
from app.stores.reminder_store import ReminderStore
from app.tools.reminder_tool import ReminderTool

router = APIRouter(prefix="/reminders", tags=["reminders"])


@router.get("/{user_id}", response_model=list[Reminder])
def list_reminders(
    user_id: str,
    store: ReminderStore = Depends(get_reminder_store),
) -> list[Reminder]:
    try:
        return store.list(user_id)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.post("/{user_id}", response_model=Reminder, status_code=201)
def create_reminder(
    user_id: str,
    payload: ReminderCreate,
    store: ReminderStore = Depends(get_reminder_store),
) -> Reminder:
    try:
        return store.add(
            user_id,
            content=payload.content,
            time=payload.time,
            recurrence=payload.recurrence,
            date=payload.date,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


@router.delete("/{user_id}/{reminder_id}", status_code=204)
def delete_reminder(
    user_id: str,
    reminder_id: str,
    store: ReminderStore = Depends(get_reminder_store),
) -> None:
    try:
        deleted = store.delete(user_id, reminder_id)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    if not deleted:
        raise HTTPException(status_code=404, detail="reminder not found")


@router.post("/{user_id}/{reminder_id}/confirm", response_model=Reminder)
def confirm_reminder(
    user_id: str,
    reminder_id: str,
    store: ReminderStore = Depends(get_reminder_store),
) -> Reminder:
    updated = store.confirm(user_id, reminder_id)
    if updated is None:
        raise HTTPException(status_code=404, detail="reminder not found")
    return updated


@router.post("/{user_id}/{reminder_id}/trigger")
def trigger_reminder(
    user_id: str,
    reminder_id: str,
    store: ReminderStore = Depends(get_reminder_store),
) -> dict:
    reminder = store.get(user_id, reminder_id)
    if reminder is None:
        raise HTTPException(status_code=404, detail="reminder not found")
    # Demo only: returns the spoken reminder; it does not place any real call.
    return {"reminder": reminder.model_dump(mode="json"), "message": ReminderTool.fire_message(reminder)}
