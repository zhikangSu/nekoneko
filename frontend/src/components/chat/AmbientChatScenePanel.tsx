"use client";

import { useEffect, useMemo, useState } from "react";

import { getMemory } from "@/lib/apiClient";
import { DEFAULT_USER_ID } from "@/lib/constants";
import {
  buildAmbientChatScenes,
  type AmbientChatScene,
} from "@/lib/proactiveTopics";

export function AmbientChatScenePanel({
  onDismiss,
  onSceneReady,
}: {
  onDismiss: (scene: AmbientChatScene) => void;
  onSceneReady: (scene: AmbientChatScene) => void;
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

  useEffect(() => {
    if (!hidden && activeScene) onSceneReady(activeScene);
  }, [activeScene, hidden, onSceneReady]);

  if (hidden || !activeScene) return null;

  function dismissCurrentScene() {
    if (activeScene) onDismiss(activeScene);
    setHidden(true);
  }

  return (
    <section
      aria-label="正在聊的话题场"
      className="rounded-2xl border border-companion/20 bg-surface shadow-sm"
    >
      <div className="flex flex-col gap-3 border-b border-black/5 px-5 py-4 lg:flex-row lg:items-start lg:justify-between">
        <div className="min-w-0">
          <div className="flex flex-wrap items-center gap-2">
            <span className="rounded-full bg-companion/10 px-3 py-1 text-sm font-semibold text-companion">
              正在聊
            </span>
            <span className="text-sm font-medium text-muted">
              {activeScene.sourceLabel}
            </span>
          </div>
          <h2 className="mt-2 text-xl font-semibold leading-snug text-ink">
            {activeScene.headline}
          </h2>
          <p className="mt-1 text-base leading-relaxed text-muted">
            {activeScene.interestAnchor}
          </p>
        </div>
        <button
          type="button"
          onClick={dismissCurrentScene}
          className="min-h-11 shrink-0 rounded-xl border border-black/10 bg-canvas px-5 text-base font-semibold text-muted hover:text-ink"
        >
          不感兴趣
        </button>
      </div>

      <div className="space-y-3 bg-[#f1f8f4] px-5 py-4">
        {activeScene.roleMessages.map((message) => (
          <div
            key={`${activeScene.id}-${message.role_label}`}
            className="flex flex-col gap-1 sm:max-w-[82%]"
          >
            <div className="text-sm font-semibold text-companion">
              {message.role_label}
            </div>
            <p className="rounded-2xl rounded-tl-sm border border-black/5 bg-surface px-4 py-3 text-base leading-relaxed text-ink">
              {message.text}
            </p>
          </div>
        ))}
      </div>
    </section>
  );
}
