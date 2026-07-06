"use client";

import { useState } from "react";

import { actOnMemoryCard } from "@/lib/apiClient";
import { DEFAULT_USER_ID } from "@/lib/constants";
import type {
  CandidateType,
  MemoryCard,
  MemoryCardAction,
  Sensitivity,
} from "@/types/memory";

const CANDIDATE_LABELS: Record<CandidateType, string> = {
  interest: "兴趣",
  fact: "事实",
  emotion: "情感",
  sensitive: "敏感",
  boundary_preference: "边界偏好",
};

const SENSITIVITY_LABELS: Record<Sensitivity, string> = {
  low: "低敏感",
  medium: "中敏感",
  high: "高敏感",
};

// Subtle tint per sensitivity so high-sensitivity cards read as more careful.
const SENSITIVITY_CLASSES: Record<Sensitivity, string> = {
  low: "bg-companion-soft text-companion",
  medium: "bg-companion-soft text-companion",
  high: "bg-caution-soft text-caution",
};

interface MemoryCardPromptProps {
  card: MemoryCard;
  // Called after a successful action with the updated (resolved) card, so the
  // parent can drop it from the pending list and refresh saved memories.
  onResolved: (card: MemoryCard) => void;
}

export function MemoryCardPrompt({ card, onResolved }: MemoryCardPromptProps) {
  const [editing, setEditing] = useState(false);
  const [editValue, setEditValue] = useState(card.summary);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(false);

  async function act(action: MemoryCardAction, editedSummary?: string) {
    setBusy(true);
    setError(false);
    try {
      const updated = await actOnMemoryCard(
        DEFAULT_USER_ID,
        card.card_id,
        action,
        editedSummary,
      );
      onResolved(updated);
    } catch {
      setError(true);
      setBusy(false);
    }
  }

  function handleEditThenSave() {
    const trimmed = editValue.trim();
    if (!trimmed) return;
    void act("edit_then_save", trimmed);
  }

  return (
    <div className="rounded-2xl bg-surface border border-black/5 p-5 space-y-4">
      <div className="flex items-center gap-2">
        <span
          className={`rounded-full px-3 py-1 text-sm font-medium ${SENSITIVITY_CLASSES[card.sensitivity]}`}
        >
          {CANDIDATE_LABELS[card.candidate_type]} · {SENSITIVITY_LABELS[card.sensitivity]}
        </span>
      </div>

      <div className="space-y-1">
        <p className="text-lg text-ink">
          我听到您提到：
          <span className="font-semibold">{card.summary}</span>
        </p>
        <p className="text-lg text-ink">
          这可以帮助我以后更好地接上这个话题。您希望我记住吗？
        </p>
        {card.why_save ? (
          <p className="text-muted text-base">{card.why_save}</p>
        ) : null}
      </div>

      {editing ? (
        <div className="space-y-2">
          <label
            htmlFor={`edit-${card.card_id}`}
            className="block text-base text-ink"
          >
            修改后再保存
          </label>
          <textarea
            id={`edit-${card.card_id}`}
            value={editValue}
            onChange={(event) => setEditValue(event.target.value)}
            rows={2}
            className="w-full rounded-xl border border-black/10 bg-canvas px-4 py-3 text-lg focus:border-companion"
          />
          <div className="flex gap-2">
            <button
              type="button"
              onClick={handleEditThenSave}
              disabled={busy || !editValue.trim()}
              className="rounded-xl bg-companion px-6 py-3 text-lg font-semibold text-white disabled:opacity-50"
            >
              保存修改
            </button>
            <button
              type="button"
              onClick={() => {
                setEditing(false);
                setEditValue(card.summary);
              }}
              disabled={busy}
              className="rounded-xl px-6 py-3 text-lg font-semibold bg-companion-soft text-companion disabled:opacity-50"
            >
              取消
            </button>
          </div>
        </div>
      ) : (
        <div className="flex flex-wrap gap-2">
          <button
            type="button"
            onClick={() => void act("save")}
            disabled={busy}
            className="rounded-xl bg-companion px-5 py-3 text-lg font-semibold text-white disabled:opacity-50"
          >
            保存
          </button>
          <button
            type="button"
            onClick={() => {
              setEditValue(card.summary);
              setEditing(true);
            }}
            disabled={busy}
            className="rounded-xl px-5 py-3 text-lg font-semibold bg-companion-soft text-companion disabled:opacity-50"
          >
            修改后保存
          </button>
          <button
            type="button"
            onClick={() => void act("reject")}
            disabled={busy}
            className="rounded-xl px-5 py-3 text-lg font-semibold bg-canvas border border-black/10 text-ink disabled:opacity-50"
          >
            不保存
          </button>
          <button
            type="button"
            onClick={() => void act("never_mention")}
            disabled={busy}
            className="rounded-xl px-5 py-3 text-lg font-semibold bg-caution-soft text-caution disabled:opacity-50"
          >
            以后不要再提
          </button>
        </div>
      )}

      {error ? (
        <p className="text-caution text-base">操作没成功，请再试一次。</p>
      ) : null}
    </div>
  );
}
