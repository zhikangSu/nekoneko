import type { AgentTrace } from "./trace";

export type CompanionMode = "role_first" | "neutral_assistant";
export type RoleSelectionMode = "auto" | "manual";
export type StudyCondition =
  | "c1_direct_question"
  | "c2_fixed_role_prelude"
  | "c3_relationship_aware";
export type ElderControlAction =
  | "continue_session"
  | "change_topic"
  | "pause_roles"
  | "stop_reminiscence";
export type MaterialType = "topic_card" | "photo" | "object" | "song";
export type RelationshipRoleId =
  | "same_age_peer"
  | "curious_junior"
  | "middle_age_bridge"
  | "elder_mentor"
  | "theme_companion"
  | "memory_organizer"
  | "boundary_guardian"
  | "no_ai_role";

export interface ChatRequest {
  user_id: string;
  message: string;
  mode: CompanionMode;
  role_selection_mode?: RoleSelectionMode;
  selected_role_ids?: RelationshipRoleId[];
  topic_id?: string | null;
  topic_label?: string | null;
  material_type?: MaterialType | null;
  study_condition?: StudyCondition;
  study_session_id?: string | null;
  elder_control_action?: ElderControlAction;
  voice_enabled?: boolean;
  sensor_preset_id?: string | null;
  companion_display_name?: string | null;
}

export interface RoleCueMessage {
  role_id: RelationshipRoleId | null;
  role_label: string;
  text: string;
}

export interface TopicMaterialContext {
  topic_id: string;
  topic_label: string;
  material_type: MaterialType;
  sensitivity: "low" | "medium" | "high";
}

export interface ChatResponse {
  turn_id: string;
  response_text: string;
  role_messages: RoleCueMessage[];
  audio_url: string | null;
  agent_trace: AgentTrace;
}

// --- Voice I/O (#4) ---------------------------------------------------------

export interface ASRResponse {
  transcript: string;
  confidence: number;
  // False when nothing was recognized — UI shows a gentle retry prompt.
  ok: boolean;
  provider: string;
  is_mock: boolean;
}

export interface TTSResponse {
  audio_base64: string;
  content_type: string;
  provider: string;
  voice: string;
  cached: boolean;
  is_mock: boolean;
}

export type MessageRole = "user" | "companion";

export interface ChatMessage {
  id: string;
  role: MessageRole;
  text: string;
  // Present on companion replies; drives the Agent Trace Panel.
  trace?: AgentTrace;
  roleMessages?: RoleCueMessage[];
  topic?: TopicMaterialContext | null;
  // True for a friendly local fallback message (e.g. backend unreachable).
  isError?: boolean;
}
