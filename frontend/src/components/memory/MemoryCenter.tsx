"use client";

import { useCallback, useEffect, useState } from "react";

import {
  addMemory,
  deleteMemory,
  getMemory,
  listMemoryCards,
  setMemoryPaused,
} from "@/lib/apiClient";
import { DEFAULT_USER_ID } from "@/lib/constants";
import type { MemoryCard, MemoryCategory, MemoryEntry } from "@/types/memory";
import { MemoryCardPrompt } from "./MemoryCardPrompt";

type VisibleMemoryCategory = Exclude<MemoryCategory, "reminder_or_setting">;

const CATEGORY_LABELS: Record<VisibleMemoryCategory, string> = {
  profile_preference: "偏好",
  event_memory: "事件",
  boundary_preference: "边界偏好",
};
const CATEGORY_ORDER: VisibleMemoryCategory[] = [
  "profile_preference",
  "event_memory",
  "boundary_preference",
];

export function MemoryCenter() {
  const [memories, setMemories] = useState<MemoryEntry[]>([]);
  const [pendingCards, setPendingCards] = useState<MemoryCard[]>([]);
  const [paused, setPaused] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [draft, setDraft] = useState("");

  const refresh = useCallback(async () => {
    try {
      const [view, cards] = await Promise.all([
        getMemory(DEFAULT_USER_ID),
        listMemoryCards(DEFAULT_USER_ID, "pending"),
      ]);
      setMemories(view.memories);
      setPendingCards(cards.cards);
      setPaused(view.settings.extraction_paused);
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

  async function handleCardResolved(resolved: MemoryCard) {
    // Optimistically drop the resolved card from the pending list, then refresh
    // so a saved / edited / never_mention card appears in saved memories.
    setPendingCards((cards) =>
      cards.filter((c) => c.card_id !== resolved.card_id),
    );
    await refresh();
  }

  async function handleDelete(id: string) {
    await deleteMemory(DEFAULT_USER_ID, id);
    await refresh();
  }

  async function handleTogglePause() {
    await setMemoryPaused(DEFAULT_USER_ID, !paused);
    await refresh();
  }

  async function handleAdd() {
    const content = draft.trim();
    if (!content) return;
    await addMemory(DEFAULT_USER_ID, "event_memory", content);
    setDraft("");
    await refresh();
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
      <div className="rounded-2xl bg-surface border border-black/5 p-5 flex items-center justify-between gap-4">
        <div>
          <h2 className="text-lg font-semibold text-ink">记忆提取</h2>
          <p className="text-muted text-base">
            {paused ? "已暂停：我不会再自动记住新的偏好。" : "开启：我会记住您明确说过的偏好。"}
          </p>
        </div>
        <button
          type="button"
          onClick={() => void handleTogglePause()}
          className="shrink-0 rounded-xl px-5 py-3 text-lg font-semibold bg-companion-soft text-companion"
        >
          {paused ? "恢复记忆" : "暂停记忆"}
        </button>
      </div>

      {pendingCards.length > 0 ? (
        <section className="space-y-3">
          <div>
            <h2 className="text-lg font-semibold text-ink">待确认的回忆卡片</h2>
            <p className="text-muted text-base">
              这些还没有保存。您来决定要不要记住，我只在您同意后才记下来。
            </p>
          </div>
          {pendingCards.map((card) => (
            <MemoryCardPrompt
              key={card.card_id}
              card={card}
              onResolved={(updated) => void handleCardResolved(updated)}
            />
          ))}
        </section>
      ) : null}

      {CATEGORY_ORDER.map((category) => {
        const items = memories.filter((m) => m.category === category);
        return (
          <section key={category}>
            <h3 className="text-lg font-semibold text-ink mb-2">
              {CATEGORY_LABELS[category]}
            </h3>
            {items.length === 0 ? (
              <p className="text-muted text-base">（暂无）</p>
            ) : (
              <ul className="space-y-2">
                {items.map((m) => (
                  <li
                    key={m.id}
                    className="flex items-center justify-between gap-3 rounded-xl bg-surface border border-black/5 px-4 py-3"
                  >
                    <span className="text-lg text-ink">{m.content}</span>
                    <button
                      type="button"
                      onClick={() => void handleDelete(m.id)}
                      className="shrink-0 rounded-lg px-4 py-2 text-base text-caution hover:bg-caution-soft"
                    >
                      删除
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </section>
        );
      })}

      <div className="rounded-2xl bg-surface border border-black/5 p-5">
        <label htmlFor="add-memory" className="block text-lg text-ink mb-1">
          手动添加一条要记住的事
        </label>
        <div className="flex gap-2">
          <input
            id="add-memory"
            value={draft}
            onChange={(event) => setDraft(event.target.value)}
            placeholder="例如：孙女周日来访"
            className="flex-1 rounded-xl border border-black/10 bg-canvas px-4 py-3 text-lg focus:border-companion"
          />
          <button
            type="button"
            onClick={() => void handleAdd()}
            disabled={!draft.trim()}
            className="rounded-xl bg-companion px-6 py-3 text-lg font-semibold text-white disabled:opacity-50"
          >
            添加
          </button>
        </div>
      </div>
    </div>
  );
}
