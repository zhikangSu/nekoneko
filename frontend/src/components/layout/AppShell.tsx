"use client";

import { useState, type ReactNode } from "react";

import { COMPANION_FALLBACK_NAME } from "@/lib/constants";
import { useProfile } from "@/components/profile/ProfileProvider";
import { ProfileSettingsDialog } from "@/components/profile/ProfileSettingsDialog";

// Header shows the companion's display name from the user profile (#21). When no
// name is set yet, it shows the neutral fallback — never an invented default.
export function AppShell({ children }: { children: ReactNode }) {
  const { companionDisplayName } = useProfile();
  const [settingsOpen, setSettingsOpen] = useState(false);

  const title =
    companionDisplayName && companionDisplayName.trim()
      ? companionDisplayName.trim()
      : COMPANION_FALLBACK_NAME;

  return (
    <div className="min-h-screen flex flex-col">
      <header className="bg-surface border-b border-black/5">
        <div className="mx-auto max-w-5xl px-5 py-4 flex items-center gap-3">
          <span
            aria-hidden
            className="h-11 w-11 shrink-0 rounded-full bg-companion-soft text-companion grid place-items-center text-xl"
          >
            🌿
          </span>
          <div className="min-w-0 flex-1">
            <h1 className="text-xl font-semibold text-ink truncate">{title}</h1>
            <p className="text-muted text-base">陪伴优先 · 放心使用</p>
          </div>
          <button
            type="button"
            onClick={() => setSettingsOpen(true)}
            className="shrink-0 rounded-xl px-4 py-2 text-base font-medium text-companion hover:bg-companion-soft"
          >
            设置
          </button>
        </div>
      </header>

      <main className="flex-1">
        <div className="mx-auto max-w-5xl px-5 py-6">{children}</div>
      </main>

      <ProfileSettingsDialog
        open={settingsOpen}
        onClose={() => setSettingsOpen(false)}
      />
    </div>
  );
}
