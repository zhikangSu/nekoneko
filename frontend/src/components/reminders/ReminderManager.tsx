"use client";

import { useCallback, useEffect, useState } from "react";

import {
  addReminder,
  confirmReminder,
  deleteReminder,
  getReminders,
  triggerReminder,
} from "@/lib/apiClient";
import { DEFAULT_USER_ID } from "@/lib/constants";
import type { Recurrence, Reminder } from "@/types/reminder";

const RECURRENCE_LABELS: Record<Recurrence, string> = {
  daily: "每天",
  once: "一次",
};

export function ReminderManager() {
  const [reminders, setReminders] = useState<Reminder[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [fired, setFired] = useState<string | null>(null);

  const [content, setContent] = useState("");
  const [time, setTime] = useState("08:00");
  const [recurrence, setRecurrence] = useState<Recurrence>("daily");

  const refresh = useCallback(async () => {
    try {
      setReminders(await getReminders(DEFAULT_USER_ID));
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

  async function handleCreate() {
    if (!content.trim() || !time) return;
    await addReminder(DEFAULT_USER_ID, { content: content.trim(), time, recurrence });
    setContent("");
    await refresh();
  }

  async function handleDelete(id: string) {
    await deleteReminder(DEFAULT_USER_ID, id);
    await refresh();
  }

  async function handleConfirm(id: string) {
    await confirmReminder(DEFAULT_USER_ID, id);
    await refresh();
  }

  async function handleTrigger(id: string) {
    const result = await triggerReminder(DEFAULT_USER_ID, id);
    setFired(result.message);
  }

  if (loading) return <p className="text-muted text-lg">正在加载…</p>;
  if (error) {
    return (
      <p className="text-caution text-lg">
        连不上后台服务，请确认后端已启动（http://localhost:8000）。
      </p>
    );
  }

  return (
    <div className="space-y-6">
      {fired ? (
        <div
          role="status"
          className="rounded-xl bg-companion-soft text-companion px-4 py-3 text-lg flex items-center justify-between gap-3"
        >
          <span>🔔 {fired}</span>
          <button
            type="button"
            onClick={() => setFired(null)}
            className="text-base text-muted hover:underline"
          >
            知道了
          </button>
        </div>
      ) : null}

      <div className="rounded-2xl bg-surface border border-black/5 p-5 space-y-3">
        <h2 className="text-lg font-semibold text-ink">添加提醒</h2>
        <div className="grid gap-3 sm:grid-cols-[1fr_auto_auto_auto] sm:items-end">
          <div>
            <label htmlFor="r-content" className="block text-base text-muted mb-1">
              提醒内容
            </label>
            <input
              id="r-content"
              value={content}
              onChange={(event) => setContent(event.target.value)}
              placeholder="例如：吃药、喝水"
              className="w-full rounded-xl border border-black/10 bg-canvas px-4 py-3 text-lg focus:border-companion"
            />
          </div>
          <div>
            <label htmlFor="r-time" className="block text-base text-muted mb-1">
              时间
            </label>
            <input
              id="r-time"
              type="time"
              value={time}
              onChange={(event) => setTime(event.target.value)}
              className="rounded-xl border border-black/10 bg-canvas px-4 py-3 text-lg focus:border-companion"
            />
          </div>
          <div>
            <label htmlFor="r-recur" className="block text-base text-muted mb-1">
              频率
            </label>
            <select
              id="r-recur"
              value={recurrence}
              onChange={(event) => setRecurrence(event.target.value as Recurrence)}
              className="rounded-xl border border-black/10 bg-canvas px-4 py-3 text-lg focus:border-companion"
            >
              <option value="daily">每天</option>
              <option value="once">一次</option>
            </select>
          </div>
          <button
            type="button"
            onClick={() => void handleCreate()}
            disabled={!content.trim()}
            className="rounded-xl bg-companion px-6 py-3 text-lg font-semibold text-white disabled:opacity-50"
          >
            添加
          </button>
        </div>
        <p className="text-muted text-base">用药提醒只负责按时提醒，具体怎么吃请按医嘱。</p>
      </div>

      <section>
        <h2 className="text-lg font-semibold text-ink mb-2">我的提醒</h2>
        {reminders.length === 0 ? (
          <p className="text-muted text-base">还没有提醒。在上面添加一个吧。</p>
        ) : (
          <ul className="space-y-2">
            {reminders.map((r) => (
              <li
                key={r.id}
                className="rounded-xl bg-surface border border-black/5 px-4 py-3 flex flex-wrap items-center justify-between gap-3"
              >
                <div className="min-w-0">
                  <div className="text-lg text-ink">
                    <span className="font-semibold tabular-nums">{r.time}</span>
                    <span className="mx-2 text-muted">·</span>
                    {RECURRENCE_LABELS[r.recurrence]}
                    {r.date ? `（${r.date}）` : ""}
                    <span className="mx-2 text-muted">·</span>
                    {r.content}
                  </div>
                  {r.last_confirmed_at ? (
                    <div className="text-base text-companion">已确认</div>
                  ) : null}
                </div>
                <div className="flex items-center gap-2">
                  <button
                    type="button"
                    onClick={() => void handleTrigger(r.id)}
                    className="rounded-lg px-4 py-2 text-base text-companion hover:bg-companion-soft"
                  >
                    试触发
                  </button>
                  <button
                    type="button"
                    onClick={() => void handleConfirm(r.id)}
                    className="rounded-lg px-4 py-2 text-base text-user hover:bg-user-soft"
                  >
                    确认
                  </button>
                  <button
                    type="button"
                    onClick={() => void handleDelete(r.id)}
                    className="rounded-lg px-4 py-2 text-base text-caution hover:bg-caution-soft"
                  >
                    删除
                  </button>
                </div>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
