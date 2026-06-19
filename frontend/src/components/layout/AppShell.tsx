"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState, type ReactNode } from "react";

import { COMPANION_FALLBACK_NAME } from "@/lib/constants";
import { useProfile } from "@/components/profile/ProfileProvider";
import { ProfileSettingsDialog } from "@/components/profile/ProfileSettingsDialog";

const NAV_ITEMS = [
  { href: "/chat", label: "聊天" },
  { href: "/memory", label: "记忆" },
  { href: "/reminders", label: "提醒" },
  { href: "/sensors", label: "关怀" },
];

function NavLink({ href, label }: { href: string; label: string }) {
  const pathname = usePathname();
  const active = pathname === href || (href === "/chat" && pathname === "/");
  return (
    <Link
      href={href}
      aria-current={active ? "page" : undefined}
      className={`rounded-xl px-4 py-2 text-lg font-medium ${
        active ? "bg-companion text-white" : "text-companion hover:bg-companion-soft"
      }`}
    >
      {label}
    </Link>
  );
}

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
        <nav
          aria-label="主导航"
          className="mx-auto max-w-5xl px-5 pb-3 flex flex-wrap gap-2"
        >
          {NAV_ITEMS.map((item) => (
            <NavLink key={item.href} href={item.href} label={item.label} />
          ))}
        </nav>
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
