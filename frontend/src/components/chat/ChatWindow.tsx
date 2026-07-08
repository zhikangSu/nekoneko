"use client";

import { useEffect, useRef, useState } from "react";

import type { VoiceControls } from "@/hooks/useVoice";
import type {
  ChatMessage,
  CompanionMode,
  RelationshipRoleId,
  RoleSelectionMode,
  StudyCondition,
  TopicMaterialContext,
} from "@/types/chat";
import { MessageBubble } from "./MessageBubble";
import { ReplayButton } from "./ReplayButton";
import { TopicCardPicker } from "./TopicCardPicker";
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

const MATERIAL_LABEL: Record<TopicMaterialContext["material_type"], string> = {
  topic_card: "话题卡",
  photo: "照片",
  object: "旧物",
  song: "音乐",
};

export function ChatWindow({
  messages,
  isSending,
  mode,
  onChangeMode,
  roleSelectionMode,
  onChangeRoleSelectionMode,
  studyCondition,
  onChangeStudyCondition,
  studySessionId,
  selectedRoleIds,
  onChangeSelectedRoleIds,
  selectedTopic,
  onChangeSelectedTopic,
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
  studyCondition: StudyCondition;
  onChangeStudyCondition: (condition: StudyCondition) => void;
  studySessionId: string;
  selectedRoleIds: RelationshipRoleId[];
  onChangeSelectedRoleIds: (roleIds: RelationshipRoleId[]) => void;
  selectedTopic: TopicMaterialContext | null;
  onChangeSelectedTopic: (topic: TopicMaterialContext | null) => void;
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
        <StudyConditionControl
          condition={studyCondition}
          onChange={onChangeStudyCondition}
          sessionId={studySessionId}
        />
        <TopicCardPicker
          selectedTopic={selectedTopic}
          onChangeSelectedTopic={onChangeSelectedTopic}
        />
      </div>

      <div ref={listRef} className="flex-1 overflow-y-auto px-5 py-4 space-y-4">
        {selectedTopic ? <SelectedTopicBanner topic={selectedTopic} /> : null}
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
      <VoiceTranscriptConfirm voice={voice} />

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
        <TTSSpeedControl voice={voice} />
      </div>
    </section>
  );
}

function SelectedTopicBanner({ topic }: { topic: TopicMaterialContext }) {
  return (
    <div className="rounded-xl border border-companion/20 bg-companion/10 px-4 py-3">
      <div className="text-sm font-semibold uppercase text-companion">
        {MATERIAL_LABEL[topic.material_type]}
      </div>
      <div className="mt-0.5 text-lg font-semibold text-ink">
        {topic.topic_id} · {topic.topic_label}
      </div>
    </div>
  );
}

function StudyConditionControl({
  condition,
  onChange,
  sessionId,
}: {
  condition: StudyCondition;
  onChange: (condition: StudyCondition) => void;
  sessionId: string;
}) {
  const options: { value: StudyCondition; label: string }[] = [
    { value: "c1_direct_question", label: "C1 直接提问" },
    { value: "c2_fixed_role_prelude", label: "C2 固定角色" },
    { value: "c3_relationship_aware", label: "C3 关系编排" },
  ];
  const shortSession = sessionId.replace(/^study_/, "").slice(0, 8);

  return (
    <div className="flex flex-wrap items-center justify-between gap-2">
      <div
        role="group"
        aria-label="研究条件"
        className="inline-flex rounded-xl bg-canvas p-1"
      >
        {options.map((option) => (
          <button
            key={option.value}
            type="button"
            onClick={() => onChange(option.value)}
            aria-pressed={condition === option.value}
            className={`rounded-lg px-3 py-1.5 text-base font-medium ${
              condition === option.value
                ? "bg-surface text-ink shadow-sm"
                : "text-muted"
            }`}
          >
            {option.label}
          </button>
        ))}
      </div>
      <span className="text-sm text-muted">Session {shortSession}</span>
    </div>
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
      className="px-5 -mb-1 pt-1 text-lg text-muted flex items-center gap-2"
    >
      {voice.recorderState === "recording" ? (
        <span aria-hidden className="h-2.5 w-2.5 rounded-full bg-companion animate-pulse" />
      ) : null}
      <span>{text}</span>
    </div>
  );
}

function VoiceTranscriptConfirm({ voice }: { voice: VoiceControls }) {
  if (!voice.pendingTranscript) return null;

  return (
    <div className="mx-5 mb-3 rounded-xl border border-companion/20 bg-companion-soft p-4">
      <div className="mb-2 flex flex-wrap items-center justify-between gap-2">
        <p className="text-lg font-semibold text-companion">
          我不太确定刚才听准了，请您确认一下。
        </p>
        <span className="text-base text-muted">
          识别置信度 {Math.round(voice.pendingTranscript.confidence * 100)}%
        </span>
      </div>
      <textarea
        value={voice.pendingTranscript.text}
        onChange={(event) => voice.editPendingTranscript(event.target.value)}
        rows={2}
        className="w-full resize-none rounded-xl border border-black/10 bg-surface px-4 py-3 text-xl leading-relaxed text-ink focus:border-companion"
      />
      <div className="mt-3 flex flex-wrap gap-2">
        <button
          type="button"
          onClick={voice.submitPendingTranscript}
          disabled={!voice.pendingTranscript.text.trim()}
          className="rounded-xl bg-companion px-5 py-2.5 text-lg font-semibold text-white disabled:opacity-50"
        >
          确认发送
        </button>
        <button
          type="button"
          onClick={voice.dismissPendingTranscript}
          className="rounded-xl border border-black/10 bg-surface px-5 py-2.5 text-lg font-semibold text-ink"
        >
          重新说
        </button>
      </div>
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

function TTSSpeedControl({ voice }: { voice: VoiceControls }) {
  const options: { value: VoiceControls["ttsSpeed"]; label: string }[] = [
    { value: 0.85, label: "慢" },
    { value: 1, label: "正常" },
    { value: 1.15, label: "稍快" },
  ];

  return (
    <div
      role="group"
      aria-label="朗读语速"
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
