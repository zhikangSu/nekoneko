// Mirrors backend app/schemas/memory.py (#10).

export type MemoryCategory =
  | "profile_preference"
  | "event_memory"
  | "reminder_or_setting"
  | "boundary_preference";

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

// --- Memory Cards (#54) -----------------------------------------------------
// Mirrors backend app/schemas/memory_card.py (authorized Memory Card workflow).

export type CandidateType =
  | "interest"
  | "fact"
  | "emotion"
  | "sensitive"
  | "boundary_preference"
  | "role_preference";

export type Sensitivity = "low" | "medium" | "high";

export type DefaultAction =
  | "suggest_save"
  | "confirm_before_save"
  | "do_not_save_by_default";

export type CardStatus =
  | "pending"
  | "saved"
  | "edited_saved"
  | "rejected"
  | "never_mention";

// The four authorized user actions on a pending card.
export type MemoryCardAction =
  | "save"
  | "edit_then_save"
  | "reject"
  | "never_mention";

export interface MemoryCard {
  card_id: string;
  user_id: string;
  candidate_type: CandidateType;
  summary: string;
  why_save: string;
  sensitivity: Sensitivity;
  default_action: DefaultAction;
  source_turn_id: string | null;
  status: CardStatus;
  created_at: string;
}

export interface MemoryCardList {
  user_id: string;
  cards: MemoryCard[];
}
