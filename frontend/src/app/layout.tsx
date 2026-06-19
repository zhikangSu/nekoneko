import type { Metadata } from "next";

import { AppShell } from "@/components/layout/AppShell";
import { ProfileProvider } from "@/components/profile/ProfileProvider";
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
          <AppShell>{children}</AppShell>
        </ProfileProvider>
      </body>
    </html>
  );
}
