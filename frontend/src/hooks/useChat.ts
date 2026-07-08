"use client";

import { useCallback, useState } from "react";

import { sendChat } from "@/lib/apiClient";
import { DEFAULT_USER_ID } from "@/lib/constants";
import type {
  ChatMessage,
  CompanionMode,
  ElderControlAction,
  RelationshipRoleId,
  RoleSelectionMode,
  StudyCondition,
  TopicMaterialContext,
} from "@/types/chat";

const DEFAULT_STUDY_CONDITION: StudyCondition = "c3_relationship_aware";
const DEFAULT_COMPANION_MODE: CompanionMode = "role_first";

function newId(): string {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
    return crypto.randomUUID();
  }
  return `m_${Date.now()}_${Math.floor(Math.random() * 1e6)}`;
}

export function useChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [roleSelectionMode, setRoleSelectionMode] =
    useState<RoleSelectionMode>("auto");
  const [studySessionId] = useState(() => `study_${newId()}`);
  const [elderControlAction, setElderControlAction] =
    useState<ElderControlAction>("continue_session");
  const [selectedRoleIds, setSelectedRoleIds] = useState<RelationshipRoleId[]>([
    "same_age_peer",
    "curious_junior",
  ]);
  const [selectedTopic, setSelectedTopic] =
    useState<TopicMaterialContext | null>(null);
  const [isSending, setIsSending] = useState(false);

  const send = useCallback(
    async (rawText: string) => {
      const text = rawText.trim();
      if (!text || isSending) return;

      const topic = selectedTopic;
      const userMessage: ChatMessage = { id: newId(), role: "user", text, topic };
      setMessages((prev) => [...prev, userMessage]);
      setIsSending(true);

      try {
        const response = await sendChat({
          user_id: DEFAULT_USER_ID,
          message: text,
          mode: DEFAULT_COMPANION_MODE,
          role_selection_mode: roleSelectionMode,
          selected_role_ids:
            roleSelectionMode === "manual" ? selectedRoleIds : [],
          topic_id: topic?.topic_id ?? null,
          topic_label: topic?.topic_label ?? null,
          material_type: topic?.material_type ?? null,
          study_condition: DEFAULT_STUDY_CONDITION,
          study_session_id: studySessionId,
          elder_control_action: elderControlAction,
        });
        setMessages((prev) => [
          ...prev,
          {
            id: response.turn_id || newId(),
            role: "companion",
            text: response.response_text,
            roleMessages: response.role_messages ?? [],
            topic,
            trace: response.agent_trace,
          },
        ]);
      } catch {
        // Friendly local fallback: keep the chat usable if the backend is down.
        setMessages((prev) => [
          ...prev,
          {
            id: newId(),
            role: "companion",
            text: "我现在好像连不上后台服务。请确认后端已启动（http://localhost:8000），我们再继续聊。",
            isError: true,
          },
        ]);
      } finally {
        setIsSending(false);
      }
    },
    [
      isSending,
      roleSelectionMode,
      selectedRoleIds,
      selectedTopic,
      studySessionId,
      elderControlAction,
    ],
  );

  return {
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
  };
}
