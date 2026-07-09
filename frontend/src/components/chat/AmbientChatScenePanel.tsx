"use client";

import { useEffect, useMemo, useRef, useState } from "react";

import { getMemory } from "@/lib/apiClient";
import { DEFAULT_USER_ID } from "@/lib/constants";
import {
  buildAmbientChatScenes,
  type AmbientChatScene,
} from "@/lib/proactiveTopics";
import type { RelationshipRoleId, RoleCueMessage } from "@/types/chat";

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

const AMBIENT_FALLBACK_ROLES: RoleCueMessage[] = [
  {
    role_id: "same_age_peer",
    role_label: "同龄共鸣者",
    text: "这个话题我也能接上，咱们顺着刚才那点慢慢聊。",
  },
  {
    role_id: "curious_junior",
    role_label: "晚辈好奇者",
    text: "我也想听听这里面的细节，您愿意说多少都可以。",
  },
];

function uniqueRoleKey(message: RoleCueMessage): string {
  return message.role_id ?? message.role_label;
}

function isAmbientRoleMessage(
  message: RoleCueMessage,
): message is RoleCueMessage & { role_id: RelationshipRoleId } {
  return Boolean(
    message.text.trim() &&
      message.role_label.trim() &&
      message.role_id &&
      message.role_id !== "no_ai_role",
  );
}

function ensureAmbientRoleMessages(
  scene: AmbientChatScene,
  reply: AmbientSceneReply,
): RoleCueMessage[] {
  const messages: RoleCueMessage[] = [];
  const seen = new Set<string>();

  function add(message: RoleCueMessage) {
    if (!isAmbientRoleMessage(message)) return;
    const key = uniqueRoleKey(message);
    if (seen.has(key)) return;
    seen.add(key);
    messages.push(message);
  }

  for (const message of reply.roleMessages) add(message);

  const sceneMessages = scene.roleMessages.filter(isAmbientRoleMessage);
  if (messages.length === 0 && reply.fallbackText.trim() && sceneMessages[0]) {
    add({ ...sceneMessages[0], text: reply.fallbackText.trim() });
  }

  for (const message of sceneMessages) add(message);
  for (const message of AMBIENT_FALLBACK_ROLES) add(message);

  return messages.slice(0, Math.max(2, Math.min(messages.length, 3)));
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
  const [activeSceneId, setActiveSceneId] = useState<string | null>(null);
  const [seenSceneIds, setSeenSceneIds] = useState<Set<string>>(() => new Set());
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

  useEffect(() => {
    if (scenes.length === 0) {
      if (activeSceneId !== null) setActiveSceneId(null);
      return;
    }

    const activeStillExists = activeSceneId
      ? scenes.some((scene) => scene.id === activeSceneId)
      : false;
    if (!activeStillExists) {
      const firstScene = scenes[0];
      setActiveSceneId(firstScene.id);
      setSeenSceneIds((current) => {
        if (current.has(firstScene.id)) return current;
        const next = new Set(current);
        next.add(firstScene.id);
        return next;
      });
    }
  }, [activeSceneId, scenes]);

  const activeScene = useMemo(() => {
    if (scenes.length === 0) return null;
    if (!activeSceneId) return scenes[0] ?? null;
    return scenes.find((scene) => scene.id === activeSceneId) ?? scenes[0] ?? null;
  }, [activeSceneId, scenes]);

  useEffect(() => {
    if (!activeScene) return;
    setThreadItems(roleItems(activeScene.id, activeScene.roleMessages));
  }, [activeScene]);

  useEffect(() => {
    const el = threadRef.current;
    if (el) el.scrollTo({ top: el.scrollHeight, behavior: "smooth" });
  }, [threadItems, isSceneSending]);

  if (!activeScene) return null;

  function showNextScene() {
    if (isSceneSending || scenes.length === 0 || !activeScene) return;
    const currentIndex = scenes.findIndex((scene) => scene.id === activeScene.id);
    const safeIndex = currentIndex >= 0 ? currentIndex : 0;
    const nextCandidates = [
      ...scenes.slice(safeIndex + 1),
      ...scenes.slice(0, safeIndex),
    ];
    const nextScene =
      nextCandidates.find((scene) => !seenSceneIds.has(scene.id)) ??
      nextCandidates[0] ??
      activeScene;

    setDraft("");
    setActiveSceneId(nextScene.id);
    setSeenSceneIds((current) => {
      if (current.has(nextScene.id)) return current;
      const next = new Set(current);
      next.add(nextScene.id);
      return next;
    });
  }

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    const scene = activeScene;
    const text = draft.trim();
    if (!scene || !text || isSceneSending) return;
    setDraft("");
    setThreadItems((current) => [
      ...current,
      { id: newItemId(), kind: "user", text },
    ]);
    setIsSceneSending(true);

    try {
      const reply = await onSend(scene, text);
      if (!reply) return;
      const messages = ensureAmbientRoleMessages(scene, reply);
      setThreadItems((current) => [
        ...current,
        ...roleItems(scene.id, messages),
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
          onClick={showNextScene}
          disabled={isSceneSending}
          className="min-h-11 shrink-0 rounded-xl border border-black/10 bg-canvas px-5 text-base font-semibold text-muted hover:text-ink disabled:cursor-not-allowed disabled:opacity-50"
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
          <p className="text-base text-muted">正在回复…</p>
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
