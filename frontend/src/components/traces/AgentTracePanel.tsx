"use client";

import { useCallback, useEffect, useState } from "react";

import { getTrace, listTraces } from "@/lib/apiClient";
import type { AgentTrace, TraceStep, TraceSummary } from "@/types/trace";
import { AgentToolBadge } from "./AgentToolBadge";
import { TraceHistory } from "./TraceHistory";

// Renders the latest turn's trace and a clickable history list (#9). Selecting a
// past turn loads its full trace; "返回最新一轮" goes back to the live one.
export function AgentTracePanel({
  latestTrace,
  userId,
  refreshKey,
}: {
  latestTrace?: AgentTrace;
  userId: string;
  refreshKey: number;
}) {
  const [history, setHistory] = useState<TraceSummary[]>([]);
  const [selected, setSelected] = useState<AgentTrace | null>(null);

  // Refresh history after each new turn; clear any historical selection.
  useEffect(() => {
    let active = true;
    listTraces(userId, 10)
      .then((rows) => active && setHistory(rows))
      .catch(() => active && setHistory([]));
    setSelected(null);
    return () => {
      active = false;
    };
  }, [userId, refreshKey]);

  const openTurn = useCallback(async (turnId: string) => {
    try {
      const record = await getTrace(turnId);
      setSelected(record.trace);
    } catch {
      /* ignore — keep showing the current trace */
    }
  }, []);

  const shown = selected ?? latestTrace;
  const viewingHistory = selected !== null;

  return (
    <aside className="rounded-2xl bg-surface border border-black/5 p-5">
      <div className="flex items-center justify-between gap-2">
        <h2 className="text-lg font-semibold text-ink">Agent Trace</h2>
        {viewingHistory ? (
          <button
            type="button"
            onClick={() => setSelected(null)}
            className="text-base text-companion hover:underline"
          >
            ← 返回最新一轮
          </button>
        ) : null}
      </div>
      <p className="text-muted text-base mt-1">
        每一轮对话经过哪些 Agent、Tool、Guard。
      </p>

      {!shown ? (
        <p className="text-muted text-base mt-4">
          发送一条消息后，这里会显示这一轮的路由与处理过程。
        </p>
      ) : (
        <div className="mt-4">
          <TraceView trace={shown} />
        </div>
      )}

      <div className="mt-4">
        <TraceHistory
          rows={history}
          activeTurnId={shown?.turn_id}
          onSelect={openTurn}
        />
      </div>
    </aside>
  );
}

function TraceView({ trace }: { trace: AgentTrace }) {
  return (
    <div className="space-y-4">
      <dl className="grid grid-cols-2 gap-x-3 gap-y-2 text-base">
        <dt className="text-muted">Route</dt>
        <dd className="text-ink font-medium">{trace.route}</dd>
        <dt className="text-muted">Risk</dt>
        <dd className="text-ink font-medium">{trace.risk_level}</dd>
        <dt className="text-muted">Mode</dt>
        <dd className="text-ink font-medium">{trace.mode}</dd>
      </dl>

      <div className="flex flex-wrap gap-2 text-base">
        <Flag label="Memory" on={trace.memory_used} />
        <Flag label="Retrieval" on={trace.retrieval_used} />
        <Flag label="SafetyCritic" on={trace.safety_critic_used} />
      </div>

      <ResearchMetadata metadata={trace.research_metadata} />
      <Section title="Agents" steps={trace.agents} empty="（本轮无）" />
      <Section title="Tools" steps={trace.tools} empty="（本轮无）" />
      <Section title="Guards" steps={trace.guards} empty="（本轮无）" />
      {trace.state_event ? (
        <Section title="State event" steps={[trace.state_event]} empty="" />
      ) : null}
    </div>
  );
}

function ResearchMetadata({ metadata }: { metadata?: Record<string, unknown> }) {
  const entries = Object.entries(metadata ?? {}).filter(
    ([, value]) => value !== null && value !== undefined && value !== "",
  );
  if (entries.length === 0) return null;

  return (
    <div>
      <h3 className="text-base font-semibold text-muted uppercase tracking-wide">
        Research
      </h3>
      <dl className="mt-1 space-y-1 text-base">
        {entries.map(([key, value]) => (
          <div key={key} className="grid grid-cols-[7rem_1fr] gap-2">
            <dt className="text-muted">{key}</dt>
            <dd className="min-w-0 break-words text-ink">
              {formatMetadataValue(value)}
            </dd>
          </div>
        ))}
      </dl>
    </div>
  );
}

function formatMetadataValue(value: unknown): string {
  if (Array.isArray(value)) return value.join(", ");
  if (typeof value === "object" && value !== null) {
    return JSON.stringify(value);
  }
  return String(value);
}

function StepRow({ step }: { step: TraceStep }) {
  return (
    <li className="flex items-start gap-2 py-1.5">
      <AgentToolBadge kind={step.kind} />
      <div className="min-w-0">
        <div className="font-medium text-ink">{step.name}</div>
        {step.summary ? (
          <div className="text-muted text-base leading-snug">{step.summary}</div>
        ) : null}
      </div>
    </li>
  );
}

function Section({
  title,
  steps,
  empty,
}: {
  title: string;
  steps: TraceStep[];
  empty: string;
}) {
  return (
    <div>
      <h3 className="text-base font-semibold text-muted uppercase tracking-wide">
        {title}
      </h3>
      {steps.length === 0 ? (
        <p className="text-muted text-base">{empty}</p>
      ) : (
        <ul>
          {steps.map((step, index) => (
            <StepRow key={`${step.kind}-${step.name}-${index}`} step={step} />
          ))}
        </ul>
      )}
    </div>
  );
}

function Flag({ label, on }: { label: string; on: boolean }) {
  return (
    <span
      className={`rounded-md px-2 py-0.5 ${
        on ? "bg-companion-soft text-companion" : "bg-black/5 text-muted"
      }`}
    >
      {label}: {on ? "on" : "off"}
    </span>
  );
}
