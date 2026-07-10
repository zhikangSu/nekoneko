"use client";

import { useCallback, useState } from "react";

import { sendChat } from "@/lib/apiClient";
import { DEFAULT_USER_ID } from "@/lib/constants";
import type {
  ChatMessage,
  ChatResponse,
  CompanionMode,
  ElderControlAction,
  MemoryScope,
  RelationshipRoleId,
  RoleSelectionMode,
  StudyCondition,
  TopicMaterialContext,
} from "@/types/chat";

const DEFAULT_STUDY_CONDITION: StudyCondition = "c3_relationship_aware";
const DEFAULT_COMPANION_MODE: CompanionMode = "role_first";
const DEFAULT_ELDER_CONTROL_ACTION: ElderControlAction = "continue_session";
const TOPIC_CARD_STARTER_TEXT = "聊这个吧";

export interface DetachedChatResult {
  text: string;
  topic: TopicMaterialContext | null;
  response: ChatResponse;
}

function newId(): string {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
    return crypto.randomUUID();
  }
  return `m_${Date.now()}_${Math.floor(Math.random() * 1e6)}`;
}

function visibleCompanionText(response: ChatResponse): string {
  const roleMessages = response.role_messages ?? [];
  if (roleMessages.length === 0) return response.response_text;
  return roleMessages
    .map((message) => `${message.role_label}：${message.text}`)
    .join("\n");
}

export function useChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [roleSelectionMode, setRoleSelectionMode] =
    useState<RoleSelectionMode>("auto");
  const [studySessionId] = useState(() => `study_${newId()}`);
  const [detachedStudySessionId] = useState(() => `detached_${newId()}`);
  const [selectedRoleIds, setSelectedRoleIds] = useState<RelationshipRoleId[]>([
    "same_age_peer",
    "curious_junior",
  ]);
  const [selectedTopic, setSelectedTopic] =
    useState<TopicMaterialContext | null>(null);
  const [isSending, setIsSending] = useState(false);

  const requestChat = useCallback(
    async (
      text: string,
      topic: TopicMaterialContext | null,
      sessionId: string | null,
      memoryScope: MemoryScope,
    ): Promise<ChatResponse> => {
      return sendChat({
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
        study_session_id: sessionId,
        elder_control_action: DEFAULT_ELDER_CONTROL_ACTION,
        memory_scope: memoryScope,
      });
    },
    [roleSelectionMode, selectedRoleIds],
  );

  const send = useCallback(
    async (
      rawText: string,
      topicOverride?: TopicMaterialContext | null,
    ) => {
      const text = rawText.trim();
      if (!text || isSending) return;

      const topic =
        topicOverride === undefined ? selectedTopic : topicOverride;
      const requestedRoleIdsForTurn =
        roleSelectionMode === "manual" ? selectedRoleIds : [];
      const userMessage: ChatMessage = { id: newId(), role: "user", text, topic };
      setMessages((prev) => [...prev, userMessage]);
      setIsSending(true);

      try {
        const response = await requestChat(
          text,
          topic,
          studySessionId,
          "default",
        );
        setMessages((prev) => [
          ...prev,
          {
            id: response.turn_id || newId(),
            role: "companion",
            text: visibleCompanionText(response),
            roleMessages: response.role_messages ?? [],
            requestedRoleIds: requestedRoleIdsForTurn,
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
            requestedRoleIds: requestedRoleIdsForTurn,
          },
        ]);
      } finally {
        setIsSending(false);
      }
    },
    [
      isSending,
      selectedTopic,
      roleSelectionMode,
      selectedRoleIds,
      requestChat,
      studySessionId,
    ],
  );

  const sendDetached = useCallback(
    async (
      rawText: string,
      topicOverride?: TopicMaterialContext | null,
      studySessionIdOverride?: string | null,
    ): Promise<DetachedChatResult | null> => {
      const text = rawText.trim();
      if (!text) return null;

      const topic = topicOverride ?? null;
      const response = await requestChat(
        text,
        topic,
        studySessionIdOverride ?? detachedStudySessionId,
        "session_only",
      );
      return { text, topic, response };
    },
    [detachedStudySessionId, requestChat],
  );

  const startTopicConversation = useCallback(
    async (topic: TopicMaterialContext) => {
      if (isSending) return;

      const requestedRoleIdsForTurn =
        roleSelectionMode === "manual" ? selectedRoleIds : [];
      setSelectedTopic(topic);
      setIsSending(true);

      try {
        const response = await requestChat(
          TOPIC_CARD_STARTER_TEXT,
          topic,
          studySessionId,
          "default",
        );
        setMessages((prev) => [
          ...prev,
          {
            id: response.turn_id || newId(),
            role: "companion",
            text: visibleCompanionText(response),
            roleMessages: response.role_messages ?? [],
            requestedRoleIds: requestedRoleIdsForTurn,
            topic,
            trace: response.agent_trace,
          },
        ]);
      } catch {
        setMessages((prev) => [
          ...prev,
          {
            id: newId(),
            role: "companion",
            text: "我现在好像连不上后台服务。请确认后端已启动（http://localhost:8000），我们再继续聊。",
            isError: true,
            requestedRoleIds: requestedRoleIdsForTurn,
            topic,
          },
        ]);
      } finally {
        setIsSending(false);
      }
    },
    [isSending, roleSelectionMode, selectedRoleIds, requestChat, studySessionId],
  );

  return {
    messages,
    roleSelectionMode,
    setRoleSelectionMode,
    selectedRoleIds,
    setSelectedRoleIds,
    selectedTopic,
    setSelectedTopic,
    isSending,
    send,
    sendDetached,
    startTopicConversation,
  };
}
