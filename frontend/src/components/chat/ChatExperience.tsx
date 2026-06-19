"use client";

import { useChat } from "@/hooks/useChat";
import type { AgentTrace } from "@/types/trace";
import { AgentTracePanel } from "@/components/traces/AgentTracePanel";
import { useProfile } from "@/components/profile/ProfileProvider";
import { ChatWindow } from "./ChatWindow";
import { SafetyBanner } from "./SafetyBanner";

// Composes the chat surface: safety banner slot, chat window, and the live Agent
// Trace panel. The companion name comes from the user profile (#21); the neutral
// fallback shows until the user names it.
export function ChatExperience() {
  const { companionDisplayName } = useProfile();
  const { messages, mode, setMode, isSending, send } = useChat();

  const latestTrace: AgentTrace | undefined = [...messages]
    .reverse()
    .find((message) => message.trace)?.trace;

  return (
    <div className="space-y-5">
      <SafetyBanner />
      <div className="grid gap-5 lg:grid-cols-[1fr_22rem]">
        <ChatWindow
          messages={messages}
          isSending={isSending}
          mode={mode}
          onChangeMode={setMode}
          onSend={send}
          companionDisplayName={companionDisplayName}
        />
        <AgentTracePanel trace={latestTrace} />
      </div>
    </div>
  );
}
