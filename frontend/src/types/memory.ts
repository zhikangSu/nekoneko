// Mirrors backend app/schemas/memory.py (#10).

export type MemoryCategory =
  | "profile_preference"
  | "event_memory"
  | "reminder_or_setting";

export interface MemoryEntry {
  id: string;
  user_id: string;
  category: MemoryCategory;
  content: string;
  created_at: string;
}

export interface MemorySettings {
  extraction_paused: boolean;
}

export interface MemoryView {
  user_id: string;
  settings: MemorySettings;
  memories: MemoryEntry[];
}
