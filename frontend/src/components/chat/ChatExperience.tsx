"use client";

import { useCallback, useEffect, useRef, useState } from "react";

import { useChat } from "@/hooks/useChat";
import { useVoice } from "@/hooks/useVoice";
import type { AgentTrace } from "@/types/trace";
import { AgentTracePanel } from "@/components/traces/AgentTracePanel";
import { useProfile } from "@/components/profile/ProfileProvider";
import { DEFAULT_USER_ID } from "@/lib/constants";
import type { AmbientChatScene } from "@/lib/proactiveTopics";
import {
  AmbientChatScenePanel,
  type AmbientSceneReply,
} from "./AmbientChatScenePanel";
import { ChatWindow } from "./ChatWindow";
import { SafetyBanner } from "./SafetyBanner";

// Composes the chat surface: safety banner slot, chat window, and the live Agent
// Trace panel. The companion name comes from the user profile (#21); the neutral
// fallback shows until the user names it. Voice (#4) records into chat and reads
// replies aloud; it is an enhancement layered over the text chat.
export function ChatExperience() {
  const { companionDisplayName } = useProfile();
  const {
    messages,
    roleSelectionMode,
    setRoleSelectionMode,
    elderControlAction,
    setElderControlAction,
    selectedRoleIds,
    setSelectedRoleIds,
    selectedTopic,
    setSelectedTopic,
    isSending,
    send,
    sendDetached,
  } = useChat();
  const voice = useVoice({ onTranscript: send });
  // The Agent Trace is a demo/explainability panel (it shows the per-turn
  // routing for graders/developers), not something an elderly end user needs —
  // so it can be collapsed, which also gives the chat the full width.
  const [showTrace, setShowTrace] = useState(false);
  const [ambientTrace, setAmbientTrace] = useState<AgentTrace | undefined>();
  const [ambientTraceVersion, setAmbientTraceVersion] = useState(0);

  // Read each newly-arrived companion reply aloud when auto-read is on. Keyed by
  // message id so toggling the switch never re-reads an older reply.
  const voiceRef = useRef(voice);
  voiceRef.current = voice;
  const spokenIdRef = useRef<string | null>(null);
  useEffect(() => {
    const latest = [...messages]
      .reverse()
      .find((message) => message.role === "companion" && !message.isError);
    if (!latest || spokenIdRef.current === latest.id) return;
    spokenIdRef.current = latest.id;
    if (voiceRef.current.autoSpeak) voiceRef.current.speak(latest.text);
  }, [messages]);

  const latestMainTrace: AgentTrace | undefined = [...messages]
    .reverse()
    .find((message) => message.trace)?.trace;
  const latestTrace = latestMainTrace ?? ambientTrace;

  const handleAmbientSceneSend = useCallback(
    async (
      scene: AmbientChatScene,
      text: string,
    ): Promise<AmbientSceneReply | null> => {
      const result = await sendDetached(text, scene.topic);
      if (!result) return null;
      setAmbientTrace(result.response.agent_trace);
      setAmbientTraceVersion((version) => version + 1);
      return {
        roleMessages: result.response.role_messages ?? [],
        fallbackText: result.response.response_text,
      };
    },
    [sendDetached],
  );

  return (
    <div className="space-y-4">
      <SafetyBanner />
      {messages.length === 0 ? (
        <AmbientChatScenePanel onSend={handleAmbientSceneSend} />
      ) : null}
      <div className="flex justify-end">
        <button
          type="button"
          onClick={() => setShowTrace((v) => !v)}
          aria-pressed={showTrace}
          className="text-base text-companion hover:underline"
        >
          {showTrace ? "隐藏追踪面板 ▸" : "◂ 显示追踪面板"}
        </button>
      </div>
      <div
        className={`grid gap-5 ${
          showTrace ? "lg:grid-cols-[1fr_22rem]" : "grid-cols-1"
        }`}
      >
        <ChatWindow
          messages={messages}
          isSending={isSending}
          roleSelectionMode={roleSelectionMode}
          onChangeRoleSelectionMode={setRoleSelectionMode}
          elderControlAction={elderControlAction}
          onChangeElderControlAction={setElderControlAction}
          selectedRoleIds={selectedRoleIds}
          onChangeSelectedRoleIds={setSelectedRoleIds}
          selectedTopic={selectedTopic}
          onChangeSelectedTopic={setSelectedTopic}
          onSend={send}
          companionDisplayName={companionDisplayName}
          voice={voice}
        />
        {showTrace ? (
          <AgentTracePanel
            latestTrace={latestTrace}
            userId={DEFAULT_USER_ID}
            refreshKey={messages.length + ambientTraceVersion}
          />
        ) : null}
      </div>
    </div>
  );
}
