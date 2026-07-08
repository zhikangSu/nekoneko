"use client";

import { useEffect, useMemo, useRef, useState } from "react";

import { getMemory } from "@/lib/apiClient";
import { DEFAULT_USER_ID } from "@/lib/constants";
import {
  buildAmbientChatScenes,
  type AmbientChatScene,
} from "@/lib/proactiveTopics";
import type { RoleCueMessage } from "@/types/chat";

export interface AmbientSceneReply {
  roleMessages: RoleCueMessage[];
  fallbackText: string;
}

type AmbientThreadItem =
  | {
      id: string;
      kind: "role";
      roleLabel: string;
      text: string;
    }
  | {
      id: string;
      kind: "user";
      text: string;
    }
  | {
      id: string;
      kind: "error";
      text: string;
    };

function newItemId(): string {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
    return crypto.randomUUID();
  }
  return `ambient_${Date.now()}_${Math.floor(Math.random() * 1e6)}`;
}

function roleItems(
  sceneId: string,
  messages: RoleCueMessage[],
): AmbientThreadItem[] {
  return messages.map((message, index) => ({
    id: `${sceneId}_${message.role_label}_${index}_${newItemId()}`,
    kind: "role",
    roleLabel: message.role_label,
    text: message.text,
  }));
}

export function AmbientChatScenePanel({
  onSend,
}: {
  onSend: (
    scene: AmbientChatScene,
    text: string,
  ) => Promise<AmbientSceneReply | null>;
}) {
  const [draft, setDraft] = useState("");
  const [isSceneSending, setIsSceneSending] = useState(false);
  const [threadItems, setThreadItems] = useState<AmbientThreadItem[]>([]);
  const [scenes, setScenes] = useState(() => buildAmbientChatScenes([]));
  const [hidden, setHidden] = useState(false);
  const threadRef = useRef<HTMLDivElement>(null);

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
    if (!activeScene) return;
    setThreadItems(roleItems(activeScene.id, activeScene.roleMessages));
  }, [activeScene]);

  useEffect(() => {
    const el = threadRef.current;
    if (el) el.scrollTo({ top: el.scrollHeight, behavior: "smooth" });
  }, [threadItems, isSceneSending]);

  if (hidden || !activeScene) return null;

  function dismissCurrentScene() {
    setHidden(true);
  }

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    const text = draft.trim();
    if (!text || isSceneSending) return;
    setDraft("");
    setThreadItems((current) => [
      ...current,
      { id: newItemId(), kind: "user", text },
    ]);
    setIsSceneSending(true);

    try {
      const reply = await onSend(activeScene, text);
      if (!reply) return;
      const messages =
        reply.roleMessages.length > 0
          ? reply.roleMessages
          : [
              {
                role_id: "theme_companion" as const,
                role_label: "主题陪伴者",
                text: reply.fallbackText,
              },
            ];
      setThreadItems((current) => [
        ...current,
        ...roleItems(activeScene.id, messages),
      ]);
    } catch {
      setThreadItems((current) => [
        ...current,
        {
          id: newItemId(),
          kind: "error",
          text: "这边暂时没接上后台，等一下再试。",
        },
      ]);
    } finally {
      setIsSceneSending(false);
    }
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

      <div
        ref={threadRef}
        className="max-h-[28rem] space-y-3 overflow-y-auto bg-[#f1f8f4] px-5 py-4"
      >
        {threadItems.map((item) =>
          item.kind === "user" ? (
            <div key={item.id} className="ml-auto flex max-w-[82%] flex-col gap-1">
              <div className="text-right text-sm font-semibold text-muted">
                您
              </div>
              <p className="rounded-2xl rounded-tr-sm bg-companion px-4 py-3 text-base leading-relaxed text-white">
                {item.text}
              </p>
            </div>
          ) : item.kind === "error" ? (
            <div key={item.id} className="flex flex-col gap-1 sm:max-w-[82%]">
              <div className="text-sm font-semibold text-muted">聊天场</div>
              <p className="rounded-2xl rounded-tl-sm border border-red-100 bg-red-50 px-4 py-3 text-base leading-relaxed text-red-700">
                {item.text}
              </p>
            </div>
          ) : (
            <div key={item.id} className="flex flex-col gap-1 sm:max-w-[82%]">
              <div className="text-sm font-semibold text-companion">
                {item.roleLabel}
              </div>
              <p className="rounded-2xl rounded-tl-sm border border-black/5 bg-surface px-4 py-3 text-base leading-relaxed text-ink">
                {item.text}
              </p>
            </div>
          ),
        )}
        {isSceneSending ? (
          <p className="text-base text-muted">几位角色正在接着聊…</p>
        ) : null}
      </div>

      <form
        onSubmit={handleSubmit}
        className="flex flex-col gap-3 border-t border-black/5 px-5 py-4 sm:flex-row sm:items-end"
      >
        <label htmlFor="ambient-chat-input" className="sr-only">
          聊天场输入
        </label>
        <textarea
          id="ambient-chat-input"
          value={draft}
          onChange={(event) => setDraft(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === "Enter" && !event.shiftKey) {
              event.preventDefault();
              handleSubmit(event);
            }
          }}
          rows={1}
          placeholder="顺着这个话题说一句…"
          className="min-h-12 flex-1 resize-none rounded-xl border border-black/10 bg-canvas px-4 py-3 text-lg leading-relaxed focus:border-companion"
        />
        <button
          type="submit"
          disabled={isSceneSending || !draft.trim()}
          className="min-h-12 rounded-xl bg-companion px-6 text-base font-semibold text-white disabled:cursor-not-allowed disabled:opacity-50"
        >
          发送
        </button>
      </form>
    </section>
  );
}
