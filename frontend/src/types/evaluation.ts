import type { TraceSummary } from "./trace";

export interface EvaluationExport {
  user_id: string;
  exported_at: string;
  trace_count: number;
  route_counts: Record<string, number>;
  risk_counts: Record<string, number>;
  safety_critic_turns: number;
  retrieval_turns: number;
  rows: TraceSummary[];
}
