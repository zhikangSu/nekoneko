import type { Recurrence } from "./reminder";

export interface CaregiverReminderDigest {
  reminder_id: string;
  label: string;
  time: string;
  recurrence: Recurrence;
  status: "confirmed_today" | "pending";
  last_confirmed_at: string | null;
}

export interface CaregiverEventDigest {
  turn_id: string;
  created_at: string;
  route: string;
  risk_level: string;
  summary: string;
}

export interface CaregiverSummary {
  user_id: string;
  generated_at: string;
  active_reminders: number;
  confirmed_reminders_today: number;
  pending_reminders: number;
  proactive_events_7d: number;
  safety_events_7d: number;
  reminders: CaregiverReminderDigest[];
  proactive_events: CaregiverEventDigest[];
  safety_events: CaregiverEventDigest[];
  privacy_boundaries: string[];
}
