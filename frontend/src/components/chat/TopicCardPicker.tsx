"use client";

import { TOPIC_CARDS } from "@/lib/topicCards";
import type { TopicMaterialContext } from "@/types/chat";

export function TopicCardPicker({
  selectedTopic,
  onChangeSelectedTopic,
  disabled = false,
}: {
  selectedTopic: TopicMaterialContext | null;
  onChangeSelectedTopic: (topic: TopicMaterialContext | null) => void;
  disabled?: boolean;
}) {
  return (
    <div className="rounded-xl border border-black/10 bg-canvas px-3 py-2">
      <div className="flex items-center justify-between gap-3">
        <div className="min-w-0">
          <div className="text-base font-semibold text-ink">可选话题</div>
          <div className="truncate text-sm text-muted">
            {selectedTopic ? `已选：${selectedTopic.topic_label}` : "未选择"}
          </div>
        </div>
        {selectedTopic ? (
          <button
            type="button"
            onClick={() => onChangeSelectedTopic(null)}
            disabled={disabled}
            className="shrink-0 rounded-lg border border-black/10 bg-surface px-3 py-1.5 text-sm font-medium text-muted disabled:cursor-not-allowed disabled:opacity-50"
          >
            清除
          </button>
        ) : null}
      </div>

      <div className="mt-2 grid max-h-32 grid-cols-2 gap-2 overflow-y-auto pr-1 sm:grid-cols-3 xl:grid-cols-4">
        {TOPIC_CARDS.map((card) => {
          const selected = selectedTopic?.topic_id === card.topic_id;
          return (
            <button
              key={card.topic_id}
              type="button"
              aria-pressed={selected}
              onClick={() => onChangeSelectedTopic(selected ? null : card)}
              disabled={disabled}
              className={[
                "min-h-12 rounded-lg border px-2 py-1.5 text-left text-sm transition",
                selected
                  ? "border-companion bg-companion/10 text-companion"
                  : "border-black/10 bg-surface text-ink hover:border-companion/50",
                disabled ? "cursor-not-allowed opacity-60" : "",
              ].join(" ")}
            >
              <span className="line-clamp-2 leading-snug font-semibold">
                {card.topic_label}
              </span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
