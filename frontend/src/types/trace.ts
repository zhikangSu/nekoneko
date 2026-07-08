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
  research_metadata: Record<string, unknown>;
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
