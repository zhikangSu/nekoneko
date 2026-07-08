"use client";

import { useEffect, useRef, useState } from "react";

import type { VoiceControls } from "@/hooks/useVoice";
import type {
  ChatMessage,
  CompanionMode,
  RelationshipRoleId,
  RoleSelectionMode,
} from "@/types/chat";
import { MessageBubble } from "./MessageBubble";
import { ReplayButton } from "./ReplayButton";
import { VoiceRecorderButton } from "./VoiceRecorderButton";

const ROLE_OPTIONS: { value: RelationshipRoleId; label: string }[] = [
  { value: "same_age_peer", label: "同龄" },
  { value: "curious_junior", label: "晚辈" },
  { value: "middle_age_bridge", label: "中年" },
  { value: "elder_mentor", label: "长辈" },
  { value: "theme_companion", label: "主题" },
  { value: "memory_organizer", label: "整理" },
  { value: "boundary_guardian", label: "守护" },
  { value: "no_ai_role", label: "不需要" },
];

export function ChatWindow({
  messages,
  isSending,
  mode,
  onChangeMode,
  roleSelectionMode,
  onChangeRoleSelectionMode,
  selectedRoleIds,
  onChangeSelectedRoleIds,
  onSend,
  companionDisplayName,
  voice,
}: {
  messages: ChatMessage[];
  isSending: boolean;
  mode: CompanionMode;
  onChangeMode: (mode: CompanionMode) => void;
  roleSelectionMode: RoleSelectionMode;
  onChangeRoleSelectionMode: (mode: RoleSelectionMode) => void;
  selectedRoleIds: RelationshipRoleId[];
  onChangeSelectedRoleIds: (roleIds: RelationshipRoleId[]) => void;
  onSend: (text: string) => void;
  companionDisplayName?: string | null;
  voice: VoiceControls;
}) {
  const [draft, setDraft] = useState("");
  const listRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Scroll the messages container itself, not the window — `scrollIntoView`
    // would also scroll the page and jump down to the (taller) trace panel.
    const el = listRef.current;
    if (el) el.scrollTo({ top: el.scrollHeight, behavior: "smooth" });
  }, [messages, isSending]);

  const lastCompanionText =
    [...messages].reverse().find((m) => m.role === "companion" && !m.isError)
      ?.text ?? null;

  function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    if (!draft.trim() || isSending) return;
    onSend(draft);
    setDraft("");
  }

  return (
    <section className="rounded-2xl bg-surface border border-black/5 flex flex-col h-[78vh] min-h-[520px]">
      <div className="px-5 py-3 border-b border-black/5 space-y-3">
        <div className="flex items-center justify-between gap-3">
          <h2 className="text-lg font-semibold text-ink">聊天</h2>
          <ModeToggle mode={mode} onChange={onChangeMode} />
        </div>
        <RoleSelectionControl
          mode={roleSelectionMode}
          onChangeMode={onChangeRoleSelectionMode}
          selectedRoleIds={selectedRoleIds}
          onChangeSelectedRoleIds={onChangeSelectedRoleIds}
        />
      </div>

      <div ref={listRef} className="flex-1 overflow-y-auto px-5 py-4 space-y-4">
        {messages.length === 0 ? (
          <p className="text-muted text-lg">
            您好，想和我说点什么都可以。可以先打个招呼，或者说说今天过得怎么样。
          </p>
        ) : (
          messages.map((message) => (
            <MessageBubble
              key={message.id}
              message={message}
              companionDisplayName={companionDisplayName}
            />
          ))
        )}
        {isSending ? (
          <p className="text-muted text-base">我听到了，正在想…</p>
        ) : null}
      </div>

      <VoiceStatus voice={voice} />

      <form
        onSubmit={handleSubmit}
        className="border-t border-black/5 px-5 py-4 flex items-end gap-3"
      >
        <VoiceRecorderButton
          supported={voice.recordingSupported}
          state={voice.recorderState}
          disabled={isSending}
          onStart={voice.startRecording}
          onStop={voice.stopRecording}
        />
        <label htmlFor="chat-input" className="sr-only">
          输入消息
        </label>
        <textarea
          id="chat-input"
          value={draft}
          onChange={(event) => setDraft(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === "Enter" && !event.shiftKey) {
              event.preventDefault();
              handleSubmit(event);
            }
          }}
          rows={1}
          placeholder="在这里输入文字…"
          className="flex-1 resize-none rounded-xl border border-black/10 bg-canvas px-4 py-3 text-lg leading-relaxed focus:border-companion"
        />
        <button
          type="submit"
          disabled={isSending || !draft.trim()}
          className="h-14 rounded-xl bg-companion px-7 text-lg font-semibold text-white disabled:opacity-50 disabled:cursor-not-allowed"
        >
          发送
        </button>
      </form>

      <div className="px-5 pb-3 -mt-1 flex flex-wrap items-center justify-between gap-x-3 gap-y-2">
        <ReplayButton
          text={lastCompanionText}
          isSpeaking={voice.isSpeaking}
          isMockVoice={voice.isMockVoice}
          onPlay={() => lastCompanionText && voice.speak(lastCompanionText)}
          onStop={voice.stopSpeaking}
        />
        <AutoSpeakToggle
          on={voice.autoSpeak}
          onChange={voice.setAutoSpeak}
        />
      </div>
    </section>
  );
}

function RoleSelectionControl({
  mode,
  onChangeMode,
  selectedRoleIds,
  onChangeSelectedRoleIds,
}: {
  mode: RoleSelectionMode;
  onChangeMode: (mode: RoleSelectionMode) => void;
  selectedRoleIds: RelationshipRoleId[];
  onChangeSelectedRoleIds: (roleIds: RelationshipRoleId[]) => void;
}) {
  const modeOptions: { value: RoleSelectionMode; label: string }[] = [
    { value: "auto", label: "系统分配" },
    { value: "manual", label: "自选角色" },
  ];

  function toggleRole(roleId: RelationshipRoleId) {
    if (roleId === "no_ai_role") {
      onChangeSelectedRoleIds(["no_ai_role"]);
      return;
    }

    const withoutNoAi = selectedRoleIds.filter((id) => id !== "no_ai_role");
    if (withoutNoAi.includes(roleId)) {
      if (withoutNoAi.length === 1) return;
      onChangeSelectedRoleIds(withoutNoAi.filter((id) => id !== roleId));
      return;
    }

    const next =
      withoutNoAi.length >= 3
        ? [...withoutNoAi.slice(1), roleId]
        : [...withoutNoAi, roleId];
    onChangeSelectedRoleIds(next);
  }

  return (
    <div className="flex flex-wrap items-center gap-2">
      <div
        role="group"
        aria-label="关系角色分配"
        className="inline-flex shrink-0 rounded-xl bg-canvas p-1"
      >
        {modeOptions.map((option) => (
          <button
            key={option.value}
            type="button"
            onClick={() => onChangeMode(option.value)}
            aria-pressed={mode === option.value}
            className={`rounded-lg px-3 py-1.5 text-base font-medium ${
              mode === option.value
                ? "bg-surface text-ink shadow-sm"
                : "text-muted"
            }`}
          >
            {option.label}
          </button>
        ))}
      </div>

      {mode === "manual" ? (
        <div className="grid w-full min-w-0 grid-cols-4 gap-1.5 sm:flex-1 sm:grid-cols-8">
          {ROLE_OPTIONS.map((role) => {
            const selected = selectedRoleIds.includes(role.value);
            return (
              <button
                key={role.value}
                type="button"
                onClick={() => toggleRole(role.value)}
                aria-pressed={selected}
                className={`min-h-9 rounded-lg border px-2 text-sm font-medium ${
                  selected
                    ? "border-companion bg-companion/10 text-companion"
                    : "border-black/10 bg-canvas text-muted"
                }`}
              >
                {role.label}
              </button>
            );
          })}
        </div>
      ) : null}
    </div>
  );
}

function VoiceStatus({ voice }: { voice: VoiceControls }) {
  let text: string | null = null;
  if (voice.recorderState === "recording") {
    text = "正在录音，说完点一下停止…";
  } else if (voice.recorderState === "transcribing") {
    text = "正在识别您说的话…";
  } else if (voice.hint) {
    text = voice.hint;
  }
  if (!text) return null;

  return (
    <div
      role="status"
      className="px-5 -mb-1 pt-1 text-base text-muted flex items-center gap-2"
    >
      {voice.recorderState === "recording" ? (
        <span aria-hidden className="h-2.5 w-2.5 rounded-full bg-companion animate-pulse" />
      ) : null}
      <span>{text}</span>
    </div>
  );
}

function AutoSpeakToggle({
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

function ModeToggle({
  mode,
  onChange,
}: {
  mode: CompanionMode;
  onChange: (mode: CompanionMode) => void;
}) {
  const options: { value: CompanionMode; label: string }[] = [
    { value: "role_first", label: "陪伴优先" },
    { value: "neutral_assistant", label: "助理模式" },
  ];
  return (
    <div
      role="group"
      aria-label="对话模式"
      className="inline-flex rounded-xl bg-canvas p-1"
    >
      {options.map((option) => (
        <button
          key={option.value}
          type="button"
          onClick={() => onChange(option.value)}
          aria-pressed={mode === option.value}
          className={`rounded-lg px-3 py-1.5 text-base font-medium ${
            mode === option.value
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
