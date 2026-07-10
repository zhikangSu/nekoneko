"use client";

import { createContext, useContext, type ReactNode } from "react";

import { useChat } from "@/hooks/useChat";

type ChatStateContextValue = ReturnType<typeof useChat>;

const ChatStateContext = createContext<ChatStateContextValue | null>(null);

export function useChatState(): ChatStateContextValue {
  const value = useContext(ChatStateContext);
  if (!value) {
    throw new Error("useChatState must be used within a ChatStateProvider");
  }
  return value;
}

export function ChatStateProvider({ children }: { children: ReactNode }) {
  const chat = useChat();
  return (
    <ChatStateContext.Provider value={chat}>
      {children}
    </ChatStateContext.Provider>
  );
}
