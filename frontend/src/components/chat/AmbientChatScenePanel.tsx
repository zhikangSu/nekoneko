"use client";

import { useEffect, useMemo, useState } from "react";

import { getMemory } from "@/lib/apiClient";
import { DEFAULT_USER_ID } from "@/lib/constants";
import {
  buildAmbientChatScenes,
  type AmbientChatScene,
} from "@/lib/proactiveTopics";

export function AmbientChatScenePanel({
  isSending,
  onJoin,
}: {
  isSending: boolean;
  onJoin: (scene: AmbientChatScene) => void;
}) {
  const [scenes, setScenes] = useState(() => buildAmbientChatScenes([]));
  const [hidden, setHidden] = useState(false);

  useEffect(() => {
    let cancelled = false;
    getMemory(DEFAULT_USER_ID)
      .then((view) => {
        if (!cancelled) setScenes(buildAmbientChatScenes(view.memories));
      })
      .catch(() => {
        if (!cancelled) setScenes(buildAmbientChatScenes([]));
      });
    return () => {
      cancelled = true;
    };
  }, []);

  const activeScene = useMemo(() => scenes[0] ?? null, [scenes]);

  if (hidden || !activeScene) return null;

  function dismissCurrentScene() {
    setHidden(true);
  }

  function joinCurrentScene() {
    if (!activeScene || isSending) return;
    onJoin(activeScene);
    dismissCurrentScene();
  }

  return (
    <section
      aria-label="正在聊的话题场"
      className="rounded-2xl border border-companion/20 bg-[#f1f8f4] px-5 py-4 shadow-sm"
    >
      <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
        <div className="min-w-0 space-y-2">
          <div className="flex flex-wrap items-center gap-2">
            <span className="rounded-full bg-companion/10 px-3 py-1 text-sm font-semibold text-companion">
              正在聊
            </span>
            <span className="text-sm font-medium text-muted">
              {activeScene.sourceLabel}
            </span>
          </div>
          <div>
            <h2 className="text-xl font-semibold leading-snug text-ink">
              {activeScene.headline}
            </h2>
            <p className="mt-1 text-base leading-relaxed text-muted">
              {activeScene.interestAnchor}
            </p>
          </div>
        </div>
        <div className="flex shrink-0 flex-wrap gap-2">
          <button
            type="button"
            onClick={joinCurrentScene}
            disabled={isSending}
            className="min-h-11 rounded-xl bg-companion px-5 text-base font-semibold text-white disabled:cursor-not-allowed disabled:opacity-50"
          >
            加入聊聊
          </button>
          <button
            type="button"
            onClick={dismissCurrentScene}
            className="min-h-11 rounded-xl border border-black/10 bg-surface px-5 text-base font-semibold text-muted hover:text-ink"
          >
            不感兴趣
          </button>
        </div>
      </div>

      <div className="mt-4 grid gap-3 lg:grid-cols-3">
        {activeScene.roleMessages.map((message) => (
          <div
            key={`${activeScene.id}-${message.role_label}`}
            className="rounded-xl border border-black/5 bg-surface/80 px-4 py-3"
          >
            <div className="text-sm font-semibold text-companion">
              {message.role_label}
            </div>
            <p className="mt-1 text-base leading-relaxed text-ink">
              {message.text}
            </p>
          </div>
        ))}
      </div>
    </section>
  );
}
