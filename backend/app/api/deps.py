"""Shared FastAPI dependencies."""

from __future__ import annotations

from fastapi import Depends

from app.core.config import Settings, get_settings
from app.stores.conversation_history_store import ConversationHistoryStore
from app.stores.guardian_state_store import GuardianStateStore
from app.stores.memory_card_store import MemoryCardStore
from app.stores.memory_store import MemoryStore
from app.stores.profile_store import ProfileStore
from app.stores.reminder_store import ReminderStore
from app.stores.trace_store import TraceStore


_conversation_history_store = ConversationHistoryStore()


def get_profile_store(settings: Settings = Depends(get_settings)) -> ProfileStore:
    return ProfileStore(settings.resolved_profile_dir)


def get_trace_store(settings: Settings = Depends(get_settings)) -> TraceStore:
    return TraceStore(settings.resolved_trace_log_dir)


def get_conversation_history_store() -> ConversationHistoryStore:
    return _conversation_history_store


def get_memory_store(settings: Settings = Depends(get_settings)) -> MemoryStore:
    return MemoryStore(settings.resolved_memory_root)


def get_memory_card_store(
    settings: Settings = Depends(get_settings),
) -> MemoryCardStore:
    return MemoryCardStore(settings.resolved_memory_cards_dir)


def get_reminder_store(settings: Settings = Depends(get_settings)) -> ReminderStore:
    return ReminderStore(settings.resolved_reminder_dir)


def get_guardian_store(
    settings: Settings = Depends(get_settings),
) -> GuardianStateStore:
    return GuardianStateStore(settings.resolved_guardian_dir)
