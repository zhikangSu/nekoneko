import type { Metadata } from "next";

import { AmbientChatStateProvider } from "@/components/chat/AmbientChatScenePanel";
import { ChatStateProvider } from "@/components/chat/ChatStateProvider";
import { AppShell } from "@/components/layout/AppShell";
import { ProfileProvider } from "@/components/profile/ProfileProvider";
import { TraceStateProvider } from "@/components/traces/TraceStateProvider";
import "@/styles/globals.css";

export const metadata: Metadata = {
  title: "陪伴 AI / AI Companion",
  description:
    "A relationship-first voice companion AI prototype for older adults (course demo).",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="zh-CN">
      <body>
        <ProfileProvider>
          <TraceStateProvider>
            <ChatStateProvider>
              <AmbientChatStateProvider>
                <AppShell>{children}</AppShell>
              </AmbientChatStateProvider>
            </ChatStateProvider>
          </TraceStateProvider>
        </ProfileProvider>
      </body>
    </html>
  );
}
