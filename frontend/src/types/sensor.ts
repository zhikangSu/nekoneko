// Mirrors backend app/schemas/sensor.py (#22, #12).

import type { AgentTrace } from "./trace";

export interface RawSignal {
  sleep_duration_hours: number;
  steps_last_3h: number;
  heart_rate_current: number;
  heart_rate_baseline: number;
  last_interaction_hours: number;
  medication_overdue_minutes: number;
  self_reported_mood: string | null;
}

export type StateEventType =
  | "NORMAL_DAY"
  | "POOR_SLEEP"
  | "LOW_ACTIVITY"
  | "REMINDER_OVERDUE"
  | "LONG_NO_RESPONSE"
  | "LOW_MOOD_SELF_REPORT"
  | "PHYSIOLOGICAL_ANOMALY_MOCK";

export type Severity = "none" | "low" | "medium" | "high";

export interface StateEvent {
  event_type: StateEventType;
  severity: Severity;
  confidence: number;
  rationale: string;
  suggested_action: string;
  medical_claim_allowed: boolean;
  source: string;
  timestamp: string;
}

export interface SensorPreset {
  id: string;
  label: string;
  description: string;
  raw_signal: RawSignal;
}

export type GuardianDecisionType =
  | "check_in"
  | "defer"
  | "silent_log"
  | "safety_escalation";

export interface GuardianDecision {
  decision: GuardianDecisionType;
  care_proposal: string;
  restraint_critique: string;
  reason: string;
  cooldown_applied: boolean;
  cooldown_minutes: number;
  trace_visible_summary: string;
}

export interface ApplyPresetResponse {
  turn_id: string;
  raw_signal: RawSignal;
  state_event: StateEvent;
  guardian_decision: GuardianDecision;
  response_text: string;
  agent_trace: AgentTrace;
}
