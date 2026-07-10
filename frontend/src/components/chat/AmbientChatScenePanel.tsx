"use client";

import {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
  type Dispatch,
  type ReactNode,
  type SetStateAction,
} from "react";

import { getMemory } from "@/lib/apiClient";
import {
  COMPANION_FALLBACK_NAME_SHORT,
  DEFAULT_USER_ID,
} from "@/lib/constants";
import {
  buildAmbientChatScenes,
  type AmbientChatScene,
} from "@/lib/proactiveTopics";
import { useVoice, type VoiceControls } from "@/hooks/useVoice";
import type { RelationshipRoleId, RoleCueMessage } from "@/types/chat";
import type { AgentTrace } from "@/types/trace";
import { ReplayButton } from "./ReplayButton";
import { VoiceRecorderButton } from "./VoiceRecorderButton";

export interface AmbientSceneReply {
  roleMessages: RoleCueMessage[];
  fallbackText: string;
}

export type AmbientThreadItem =
  | {
      id: string;
      kind: "role";
      roleLabel: string;
      text: string;
    }
  | {
      id: string;
      kind: "companion";
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

type AmbientReplyItem = Extract<
  AmbientThreadItem,
  { kind: "role" | "companion" }
>;

interface AmbientChatStateContextValue {
  draft: string;
  setDraft: Dispatch<SetStateAction<string>>;
  isSceneSending: boolean;
  setIsSceneSending: Dispatch<SetStateAction<boolean>>;
  threadItems: AmbientThreadItem[];
  setThreadItems: Dispatch<SetStateAction<AmbientThreadItem[]>>;
  threadSceneId: string | null;
  setThreadSceneId: Dispatch<SetStateAction<string | null>>;
  scenes: AmbientChatScene[];
  setScenes: Dispatch<SetStateAction<AmbientChatScene[]>>;
  activeSceneId: string | null;
  setActiveSceneId: Dispatch<SetStateAction<string | null>>;
  seenSceneIds: Set<string>;
  setSeenSceneIds: Dispatch<SetStateAction<Set<string>>>;
  ambientTrace: AgentTrace | undefined;
  setAmbientTrace: Dispatch<SetStateAction<AgentTrace | undefined>>;
  ambientTraceVersion: number;
  setAmbientTraceVersion: Dispatch<SetStateAction<number>>;
  ambientSessionRoot: string;
}

const AmbientChatStateContext =
  createContext<AmbientChatStateContextValue | null>(null);

function newClientSessionRoot(prefix: string): string {
  return `${prefix}_${Date.now().toString(36)}_${Math.floor(
    Math.random() * 1e6,
  ).toString(36)}`;
}

function newItemId(): string {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
    return crypto.randomUUID();
  }
  return `ambient_${Date.now()}_${Math.floor(Math.random() * 1e6)}`;
}

function roleItems(
  sceneId: string,
  messages: RoleCueMessage[],
): AmbientReplyItem[] {
  return messages.map((message, index) => ({
    id: `${sceneId}_${message.role_label}_${index}_${newItemId()}`,
    kind: "role",
    roleLabel: message.role_label,
    text: message.text,
  }));
}

const ROLE_REVEAL_DELAY_MS = 850;
const INITIAL_ROLE_MESSAGE_COUNT = 2;

function delay(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

export function useAmbientChatState(): AmbientChatStateContextValue {
  const value = useContext(AmbientChatStateContext);
  if (!value) {
    throw new Error(
      "useAmbientChatState must be used within an AmbientChatStateProvider",
    );
  }
  return value;
}

export function AmbientChatStateProvider({
  children,
}: {
  children: ReactNode;
}) {
  const [draft, setDraft] = useState("");
  const [isSceneSending, setIsSceneSending] = useState(false);
  const [threadItems, setThreadItems] = useState<AmbientThreadItem[]>([]);
  const [threadSceneId, setThreadSceneId] = useState<string | null>(null);
  const [scenes, setScenes] = useState(() => buildAmbientChatScenes([]));
  const [activeSceneId, setActiveSceneId] = useState<string | null>(null);
  const [seenSceneIds, setSeenSceneIds] = useState<Set<string>>(
    () => new Set(),
  );
  const [ambientTrace, setAmbientTrace] = useState<AgentTrace | undefined>();
  const [ambientTraceVersion, setAmbientTraceVersion] = useState(0);
  const [ambientSessionRoot] = useState(() =>
    newClientSessionRoot("ambient"),
  );

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

  return (
    <AmbientChatStateContext.Provider
      value={{
        draft,
        setDraft,
        isSceneSending,
        setIsSceneSending,
        threadItems,
        setThreadItems,
        threadSceneId,
        setThreadSceneId,
        scenes,
        setScenes,
        activeSceneId,
        setActiveSceneId,
        seenSceneIds,
        setSeenSceneIds,
        ambientTrace,
        setAmbientTrace,
        ambientTraceVersion,
        setAmbientTraceVersion,
        ambientSessionRoot,
      }}
    >
      {children}
    </AmbientChatStateContext.Provider>
  );
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

function ambientReplyItems(
  sceneId: string,
  reply: AmbientSceneReply,
): AmbientReplyItem[] {
  const realRoleMessages = reply.roleMessages.filter(isAmbientRoleMessage);
  if (realRoleMessages.length > 0) {
    return roleItems(sceneId, realRoleMessages);
  }

  const text = reply.fallbackText.trim();
  if (!text) return [];
  return [{ id: newItemId(), kind: "companion", text }];
}

export function AmbientChatScenePanel({
  companionDisplayName,
  onSend,
}: {
  companionDisplayName?: string | null;
  onSend: (
    scene: AmbientChatScene,
    text: string,
  ) => Promise<AmbientSceneReply | null>;
}) {
  const companionLabel =
    companionDisplayName && companionDisplayName.trim()
      ? companionDisplayName.trim()
      : COMPANION_FALLBACK_NAME_SHORT;
  const {
    draft,
    setDraft,
    isSceneSending,
    setIsSceneSending,
    threadItems,
    setThreadItems,
    threadSceneId,
    setThreadSceneId,
    scenes,
    activeSceneId,
    setActiveSceneId,
    seenSceneIds,
    setSeenSceneIds,
  } = useAmbientChatState();
  const threadRef = useRef<HTMLDivElement>(null);
  const skipNextScrollRef = useRef(false);
  const voice = useVoice({
    onTranscript: (text) => {
      void submitText(text);
    },
  });

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
  }, [
    activeSceneId,
    scenes,
    setActiveSceneId,
    setSeenSceneIds,
  ]);

  const activeScene = useMemo(() => {
    if (scenes.length === 0) return null;
    if (!activeSceneId) return scenes[0] ?? null;
    return scenes.find((scene) => scene.id === activeSceneId) ?? scenes[0] ?? null;
  }, [activeSceneId, scenes]);

  useEffect(() => {
    if (!activeScene) return;
    if (threadSceneId === activeScene.id && threadItems.length > 0) return;
    skipNextScrollRef.current = true;
    setThreadItems(
      roleItems(
        activeScene.id,
        activeScene.roleMessages.slice(0, INITIAL_ROLE_MESSAGE_COUNT),
      ),
    );
    setThreadSceneId(activeScene.id);
  }, [
    activeScene,
    setThreadItems,
    setThreadSceneId,
    threadItems.length,
    threadSceneId,
  ]);

  useEffect(() => {
    const el = threadRef.current;
    if (skipNextScrollRef.current) {
      skipNextScrollRef.current = false;
      if (el) el.scrollTo({ top: 0 });
      return;
    }
    if (el) el.scrollTo({ top: el.scrollHeight, behavior: "smooth" });
  }, [threadItems, isSceneSending]);

  const lastReplyText = useMemo(() => {
    return (
      [...threadItems]
        .reverse()
        .find(
          (item) => item.kind === "role" || item.kind === "companion",
        )?.text ?? null
    );
  }, [threadItems]);

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

  async function appendReplyItemsSequentially(items: AmbientReplyItem[]) {
    for (const item of items) {
      setThreadItems((current) => [...current, item]);
      if (voice.autoSpeak) {
        const speaker =
          item.kind === "role" ? item.roleLabel : companionLabel;
        void voice.speak(`${speaker}：${item.text}`);
      }
      await delay(ROLE_REVEAL_DELAY_MS);
    }
  }

  async function submitText(rawText: string) {
    const scene = activeScene;
    const text = rawText.trim();
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
      await appendReplyItemsSequentially(
        ambientReplyItems(scene.id, reply),
      );
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

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    await submitText(draft);
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
        className="max-h-40 space-y-3 overflow-y-auto bg-[#f1f8f4] px-5 py-4 sm:max-h-56 lg:max-h-[28rem]"
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
                {item.kind === "role" ? item.roleLabel : companionLabel}
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
        <VoiceRecorderButton
          supported={voice.recordingSupported}
          state={voice.recorderState}
          disabled={isSceneSending}
          onStart={voice.startRecording}
          onStop={voice.stopRecording}
        />
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
          placeholder="您想到了什么，都可以慢慢说…"
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
      <AmbientVoiceStatus voice={voice} />
      <AmbientVoiceTranscriptConfirm voice={voice} />
      <div className="flex flex-wrap items-center justify-between gap-x-3 gap-y-2 px-5 pb-4">
        <ReplayButton
          text={lastReplyText}
          isSpeaking={voice.isSpeaking}
          isMockVoice={voice.isMockVoice}
          onPlay={() => lastReplyText && void voice.speak(lastReplyText)}
          onStop={voice.stopSpeaking}
        />
        <AmbientAutoSpeakToggle
          on={voice.autoSpeak}
          onChange={voice.setAutoSpeak}
        />
        <AmbientTTSSpeedControl voice={voice} />
      </div>
    </section>
  );
}

function AmbientVoiceStatus({ voice }: { voice: VoiceControls }) {
  let text: string | null = null;
  if (voice.recorderState === "recording") {
    text = "正在听您说，讲完点一下停止…";
  } else if (voice.recorderState === "transcribing") {
    text = "正在识别您说的话…";
  } else if (voice.hint) {
    text = voice.hint;
  }
  if (!text) return null;

  return (
    <div className="px-5 pb-2 text-base text-muted">
      {text}
    </div>
  );
}

function AmbientVoiceTranscriptConfirm({ voice }: { voice: VoiceControls }) {
  if (!voice.pendingTranscript) return null;

  return (
    <div className="mx-5 mb-3 rounded-xl border border-companion/20 bg-companion-soft p-4">
      <div className="mb-2 flex flex-wrap items-center justify-between gap-2">
        <p className="text-base font-semibold text-companion">
          我不太确定刚才听准了，请您确认一下。
        </p>
        <span className="text-sm text-muted">
          识别置信度 {Math.round(voice.pendingTranscript.confidence * 100)}%
        </span>
      </div>
      <textarea
        value={voice.pendingTranscript.text}
        onChange={(event) => voice.editPendingTranscript(event.target.value)}
        rows={2}
        className="w-full resize-none rounded-xl border border-black/10 bg-surface px-4 py-3 text-lg leading-relaxed text-ink focus:border-companion"
      />
      <div className="mt-3 flex flex-wrap gap-2">
        <button
          type="button"
          onClick={voice.submitPendingTranscript}
          disabled={!voice.pendingTranscript.text.trim()}
          className="rounded-xl bg-companion px-5 py-2.5 text-base font-semibold text-white disabled:opacity-50"
        >
          确认发送
        </button>
        <button
          type="button"
          onClick={voice.dismissPendingTranscript}
          className="rounded-xl border border-black/10 bg-surface px-5 py-2.5 text-base font-semibold text-ink"
        >
          重新说
        </button>
      </div>
    </div>
  );
}

function AmbientAutoSpeakToggle({
  on,
  onChange,
}: {
  on: boolean;
  onChange: (on: boolean) => void;
}) {
  return (
    <button
      type="button"
      role="switch"
      aria-checked={on}
      onClick={() => onChange(!on)}
      className="inline-flex shrink-0 items-center gap-2 whitespace-nowrap text-base text-muted"
    >
      <span
        aria-hidden
        className={`flex h-6 w-11 shrink-0 items-center rounded-full p-0.5 transition-colors ${
          on ? "justify-end bg-companion" : "justify-start bg-black/15"
        }`}
      >
        <span className="h-5 w-5 rounded-full bg-white shadow-sm" />
      </span>
      <span>自动朗读回复</span>
    </button>
  );
}

function AmbientTTSSpeedControl({ voice }: { voice: VoiceControls }) {
  const options: { value: VoiceControls["ttsSpeed"]; label: string }[] = [
    { value: 0.85, label: "慢" },
    { value: 1, label: "正常" },
    { value: 1.15, label: "稍快" },
  ];

  return (
    <div
      role="group"
      aria-label="聊天场朗读语速"
      className="inline-flex shrink-0 rounded-xl bg-canvas p-1"
    >
      {options.map((option) => (
        <button
          key={option.value}
          type="button"
          onClick={() => voice.setTtsSpeed(option.value)}
          aria-pressed={voice.ttsSpeed === option.value}
          className={`rounded-lg px-3 py-1.5 text-base font-medium ${
            voice.ttsSpeed === option.value
              ? "bg-surface text-ink shadow-sm"
              : "text-muted"
          }`}
        >
          {option.label}
        </button>
      ))}
    </div>
  );
}
