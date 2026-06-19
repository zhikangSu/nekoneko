"""SensorSimulatorTool — mock sensor presets (issues #22, #12).

Demo-only presets standing in for wearable / behavioral signals. Each preset is
a ``RawSignal`` the SensorAdapter turns into a ``StateEvent``.
"""

from __future__ import annotations

from typing import Optional

from app.schemas.sensor import RawSignal, SensorPreset

_PRESETS: tuple[SensorPreset, ...] = (
    SensorPreset(
        id="normal_day",
        label="Normal Day",
        description="一切如常",
        raw_signal=RawSignal(),
    ),
    SensorPreset(
        id="poor_sleep",
        label="Poor Sleep",
        description="睡眠明显偏少",
        raw_signal=RawSignal(sleep_duration_hours=3.5),
    ),
    SensorPreset(
        id="low_activity",
        label="Low Activity",
        description="近几小时几乎没有走动",
        raw_signal=RawSignal(steps_last_3h=40),
    ),
    SensorPreset(
        id="medication_missed",
        label="Medication Missed",
        description="用药时间已过",
        raw_signal=RawSignal(medication_overdue_minutes=90),
    ),
    SensorPreset(
        id="elevated_hr_mock",
        label="Elevated HR Mock",
        description="心率高于基线（仅模拟）",
        raw_signal=RawSignal(heart_rate_current=110, heart_rate_baseline=70),
    ),
    SensorPreset(
        id="no_response",
        label="No Response",
        description="很久没有互动",
        raw_signal=RawSignal(last_interaction_hours=10.0),
    ),
    SensorPreset(
        id="low_mood",
        label="Low Mood Self-Report",
        description="自述心情低落",
        raw_signal=RawSignal(self_reported_mood="low"),
    ),
)

_BY_ID = {preset.id: preset for preset in _PRESETS}


class SensorSimulatorTool:
    name = "SensorSimulatorTool"

    def list_presets(self) -> list[SensorPreset]:
        return list(_PRESETS)

    def get(self, preset_id: str) -> Optional[SensorPreset]:
        return _BY_ID.get(preset_id)
