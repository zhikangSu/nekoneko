"use client";

import { useEffect, useRef, useState } from "react";

import type { VoiceControls } from "@/hooks/useVoice";
import type { ChatMessage, CompanionMode } from "@/types/chat";
import { MessageBubble } from "./MessageBubble";
import { ReplayButton } from "./ReplayButton";
import { VoiceRecorderButton } from "./VoiceRecorderButton";

export function ChatWindow({
  messages,
  isSending,
  mode,
  onChangeMode,
  onSend,
  companionDisplayName,
  voice,
}: {
  messages: ChatMessage[];
  isSending: boolean;
  mode: CompanionMode;
  onChangeMode: (mode: CompanionMode) => void;
  onSend: (text: string) => void;
  companionDisplayName?: string | null;
  voice: VoiceControls;
}) {
  const [draft, setDraft] = useState("");
  const listEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    listEndRef.current?.scrollIntoView({ behavior: "smooth" });
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
      <div className="flex items-center justify-between gap-3 px-5 py-3 border-b border-black/5">
        <h2 className="text-lg font-semibold text-ink">聊天</h2>
        <ModeToggle mode={mode} onChange={onChangeMode} />
      </div>

      <div className="flex-1 overflow-y-auto px-5 py-4 space-y-4">
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
        <div ref={listEndRef} />
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
        className={`relative inline-block h-6 w-11 shrink-0 rounded-full transition-colors ${
          on ? "bg-companion" : "bg-black/15"
        }`}
      >
        <span
          className={`absolute top-0.5 h-5 w-5 rounded-full bg-white transition-transform ${
            on ? "translate-x-5" : "translate-x-0.5"
          }`}
        />
      </span>
      自动朗读回复
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
