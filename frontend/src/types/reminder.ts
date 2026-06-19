// Mirrors backend app/schemas/reminder.py (#11).

export type Recurrence = "once" | "daily";

export interface Reminder {
  id: string;
  user_id: string;
  content: string;
  time: string; // HH:MM
  recurrence: Recurrence;
  date: string | null;
  created_at: string;
  active: boolean;
  last_confirmed_at: string | null;
}

export interface ReminderCreate {
  content: string;
  time: string;
  recurrence: Recurrence;
  date?: string | null;
}
