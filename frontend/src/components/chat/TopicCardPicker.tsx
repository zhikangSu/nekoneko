"use client";

import { TOPIC_CARDS } from "@/lib/topicCards";
import type { TopicMaterialContext } from "@/types/chat";

const SENSITIVITY_LABEL: Record<TopicMaterialContext["sensitivity"], string> = {
  low: "低",
  medium: "中",
  high: "高",
};

const SENSITIVITY_STYLE: Record<TopicMaterialContext["sensitivity"], string> = {
  low: "border-emerald-200 bg-emerald-50 text-emerald-800",
  medium: "border-amber-200 bg-amber-50 text-amber-800",
  high: "border-rose-200 bg-rose-50 text-rose-800",
};

export function TopicCardPicker({
  selectedTopic,
  onChangeSelectedTopic,
}: {
  selectedTopic: TopicMaterialContext | null;
  onChangeSelectedTopic: (topic: TopicMaterialContext | null) => void;
}) {
  return (
    <div className="rounded-xl border border-black/10 bg-canvas px-3 py-2">
      <div className="flex items-center justify-between gap-3">
        <div className="min-w-0">
          <div className="text-base font-semibold text-ink">话题卡</div>
          <div className="truncate text-sm text-muted">
            {selectedTopic
              ? `${selectedTopic.topic_id} · ${selectedTopic.topic_label}`
              : "未选择"}
          </div>
        </div>
        {selectedTopic ? (
          <button
            type="button"
            onClick={() => onChangeSelectedTopic(null)}
            className="shrink-0 rounded-lg border border-black/10 bg-surface px-3 py-1.5 text-sm font-medium text-muted"
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
              onClick={() => onChangeSelectedTopic(card)}
              className={[
                "min-h-12 rounded-lg border px-2 py-1.5 text-left text-sm transition",
                selected
                  ? "border-companion bg-companion/10 text-companion"
                  : "border-black/10 bg-surface text-ink hover:border-companion/50",
              ].join(" ")}
            >
              <span className="block font-semibold">{card.topic_id}</span>
              <span className="line-clamp-2 leading-snug">{card.topic_label}</span>
              <span
                className={[
                  "mt-1 inline-flex rounded-md border px-1.5 py-0.5 text-xs",
                  SENSITIVITY_STYLE[card.sensitivity],
                ].join(" ")}
              >
                敏感度 {SENSITIVITY_LABEL[card.sensitivity]}
              </span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
