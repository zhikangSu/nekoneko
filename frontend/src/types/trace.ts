// Mirrors backend app/schemas/trace.py. Keeps the Agent / Tool / Guard
// distinction visible (AGENTS.md §5, §13).

export type TraceEntryKind =
  | "agent"
  | "tool"
  | "guard"
  | "state_event"
  | "retrieval"
  | "memory";

export interface TraceStep {
  kind: TraceEntryKind;
  name: string;
  summary?: string;
  detail?: Record<string, unknown>;
}

export interface AgentTrace {
  turn_id: string;
  mode: string;
  route: string;
  risk_level: string;
  agents: TraceStep[];
  tools: TraceStep[];
  guards: TraceStep[];
  state_event: TraceStep | null;
  memory_used: boolean;
  retrieval_used: boolean;
  safety_critic_used: boolean;
  conversation_history_used: boolean;
  conversation_history_count: number;
  conversation_seed_used: boolean;
  conversation_seed_count: number;
  research_metadata: Record<string, unknown>;
  research_trace?: ResearchTraceMetadata;
}

export interface ResearchTraceMetadata {
  interaction?: {
    intent: string | null;
    role_selection_source: string | null;
    context_role_ids: string[];
  };
  role: {
    candidate_roles?: string[];
    selected_roles: string[];
    silent_roles?: string[];
    primary_role: string | null;
    role_selection_mode: string | null;
    requested_role_ids: string[];
    cueing_style: string | null;
    allow_follow_up?: boolean;
    follow_up_reason?: string | null;
  };
  topic: {
    topic_id: string | null;
    topic_label: string | null;
    material_type: string | null;
    classified_topic: string | null;
  };
  boundary: {
    boundary_state: string;
    boundary_notes: string[];
  };
  control: {
    study_condition: string | null;
    study_session_id: string | null;
    elder_control_action: string | null;
  };
}

// A persisted trace returned by GET /api/traces/{turn_id} (#9).
export interface TraceRecord {
  turn_id: string;
  user_id: string;
  created_at: string;
  trace: AgentTrace;
}

// A compact row from GET /api/traces?user_id=&limit= (#9).
export interface TraceSummary {
  turn_id: string;
  user_id: string;
  created_at: string;
  route: string;
  risk_level: string;
  safety_critic_used: boolean;
  retrieval_used: boolean;
}
