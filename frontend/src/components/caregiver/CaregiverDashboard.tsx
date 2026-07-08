"use client";

import { useCallback, useEffect, useState } from "react";

import { getCaregiverSummary } from "@/lib/apiClient";
import { DEFAULT_USER_ID } from "@/lib/constants";
import type {
  CaregiverEventDigest,
  CaregiverReminderDigest,
  CaregiverSummary,
} from "@/types/caregiver";

const STATUS_LABELS: Record<CaregiverReminderDigest["status"], string> = {
  confirmed_today: "今日已确认",
  pending: "待确认",
};

const RECURRENCE_LABELS: Record<CaregiverReminderDigest["recurrence"], string> = {
  daily: "每天",
  once: "一次",
};

export function CaregiverDashboard() {
  const [summary, setSummary] = useState<CaregiverSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  const refresh = useCallback(async () => {
    try {
      setSummary(await getCaregiverSummary(DEFAULT_USER_ID));
      setError(false);
    } catch {
      setError(true);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  if (loading) return <p className="text-lg text-muted">正在加载…</p>;
  if (error || summary === null) {
    return (
      <p className="text-lg text-caution">
        连不上后台服务，请确认后端已启动（http://localhost:8000）。
      </p>
    );
  }

  return (
    <div className="space-y-6">
      <div className="grid gap-3 md:grid-cols-4">
        <MetricCard label="有效提醒" value={summary.active_reminders} />
        <MetricCard label="今日已确认" value={summary.confirmed_reminders_today} />
        <MetricCard label="7 日主动关怀" value={summary.proactive_events_7d} />
        <MetricCard
          label="7 日安全事件"
          value={summary.safety_events_7d}
          tone={summary.safety_events_7d > 0 ? "caution" : "normal"}
        />
      </div>

      <div className="grid gap-5 lg:grid-cols-[1fr_1fr]">
        <section className="rounded-lg border border-black/10 bg-surface p-5">
          <div className="flex flex-wrap items-end justify-between gap-2">
            <h2 className="text-xl font-semibold text-ink">提醒完成摘要</h2>
            <span className="text-sm text-muted">
              更新于 {formatDateTime(summary.generated_at)}
            </span>
          </div>
          <div className="mt-4 space-y-3">
            {summary.reminders.length === 0 ? (
              <p className="text-base text-muted">暂无有效提醒。</p>
            ) : (
              summary.reminders.map((reminder) => (
                <ReminderRow key={reminder.reminder_id} reminder={reminder} />
              ))
            )}
          </div>
        </section>

        <section className="rounded-lg border border-black/10 bg-surface p-5">
          <h2 className="text-xl font-semibold text-ink">安全与关怀摘要</h2>
          <div className="mt-4 space-y-5">
            <EventList title="主动关怀" events={summary.proactive_events} />
            <EventList title="安全事件" events={summary.safety_events} />
          </div>
        </section>
      </div>

      <section className="rounded-lg border border-black/10 bg-surface p-5">
        <h2 className="text-xl font-semibold text-ink">隐私边界</h2>
        <ul className="mt-3 grid gap-2 sm:grid-cols-3">
          {summary.privacy_boundaries.map((item) => (
            <li key={item} className="border-l-4 border-companion/50 pl-3 text-muted">
              {item}
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}

function MetricCard({
  label,
  value,
  tone = "normal",
}: {
  label: string;
  value: number;
  tone?: "normal" | "caution";
}) {
  return (
    <div
      className={`rounded-lg border p-4 ${
        tone === "caution"
          ? "border-caution/30 bg-caution-soft text-caution"
          : "border-black/10 bg-surface text-companion"
      }`}
    >
      <p className="text-sm text-muted">{label}</p>
      <p className="mt-2 text-3xl font-semibold tabular-nums">{value}</p>
    </div>
  );
}

function ReminderRow({ reminder }: { reminder: CaregiverReminderDigest }) {
  const confirmed = reminder.status === "confirmed_today";
  return (
    <div className="flex flex-wrap items-center justify-between gap-3 border-b border-black/5 pb-3 last:border-0 last:pb-0">
      <div>
        <p className="text-lg font-medium text-ink">
          {reminder.label}
          <span className="mx-2 text-muted">·</span>
          <span className="tabular-nums">{reminder.time}</span>
          <span className="mx-2 text-muted">·</span>
          {RECURRENCE_LABELS[reminder.recurrence]}
        </p>
        {reminder.last_confirmed_at ? (
          <p className="text-sm text-muted">
            最近确认 {formatDateTime(reminder.last_confirmed_at)}
          </p>
        ) : null}
      </div>
      <span
        className={`rounded-lg px-3 py-1 text-sm font-medium ${
          confirmed ? "bg-user-soft text-user" : "bg-canvas text-muted"
        }`}
      >
        {STATUS_LABELS[reminder.status]}
      </span>
    </div>
  );
}

function EventList({
  title,
  events,
}: {
  title: string;
  events: CaregiverEventDigest[];
}) {
  return (
    <div>
      <h3 className="text-lg font-medium text-ink">{title}</h3>
      {events.length === 0 ? (
        <p className="mt-2 text-base text-muted">暂无记录。</p>
      ) : (
        <ul className="mt-2 space-y-2">
          {events.map((event) => (
            <li
              key={event.turn_id}
              className="flex flex-wrap items-center justify-between gap-2 border-b border-black/5 pb-2 last:border-0 last:pb-0"
            >
              <span className="text-base text-ink">{event.summary}</span>
              <span className="text-sm text-muted">
                {event.risk_level} · {formatDateTime(event.created_at)}
              </span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

function formatDateTime(value: string) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString("zh-CN", {
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}
