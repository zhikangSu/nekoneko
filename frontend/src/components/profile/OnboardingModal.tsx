"use client";

import { useState } from "react";

import { COMPANION_FALLBACK_NAME } from "@/lib/constants";
import { useProfile } from "./ProfileProvider";

// First-run naming (#21). Asks how the user would like to address the companion
// (optional) and, optionally, how to address the user. No suggested/fixed name;
// skipping keeps the neutral fallback.
export function OnboardingModal() {
  const { update } = useProfile();
  const [companionName, setCompanionName] = useState("");
  const [userName, setUserName] = useState("");
  const [saving, setSaving] = useState(false);

  async function finish(withNames: boolean) {
    if (saving) return;
    setSaving(true);
    try {
      await update({
        onboarding_completed: true,
        ...(withNames
          ? {
              companion_display_name: companionName.trim() || null,
              user_display_name: userName.trim() || null,
            }
          : {}),
      });
    } finally {
      setSaving(false);
    }
  }

  return (
    <div
      className="fixed inset-0 z-50 grid place-items-center bg-black/30 px-4"
      role="dialog"
      aria-modal="true"
      aria-labelledby="onboarding-title"
    >
      <div className="w-full max-w-lg rounded-2xl bg-surface p-7 shadow-xl">
        <h2 id="onboarding-title" className="text-2xl font-semibold text-ink">
          您好，我是您的陪伴 AI
        </h2>
        <p className="mt-2 text-lg text-muted leading-relaxed">
          您希望怎么称呼我呢？可以给我取一个您喜欢的名字，也可以先跳过。
          不取名字也没关系，我会一直叫作「{COMPANION_FALLBACK_NAME}」。
        </p>

        <form
          className="mt-5 space-y-4"
          onSubmit={(event) => {
            event.preventDefault();
            void finish(true);
          }}
        >
          <div>
            <label
              htmlFor="companion-name"
              className="block text-lg text-ink mb-1"
            >
              您希望怎么称呼我？
            </label>
            <input
              id="companion-name"
              value={companionName}
              onChange={(event) => setCompanionName(event.target.value)}
              maxLength={40}
              placeholder="例如：阿南、老朋友…（可不填）"
              className="w-full rounded-xl border border-black/10 bg-canvas px-4 py-3 text-lg focus:border-companion"
            />
          </div>

          <div>
            <label htmlFor="user-name" className="block text-lg text-ink mb-1">
              我可以怎么称呼您？（可不填）
            </label>
            <input
              id="user-name"
              value={userName}
              onChange={(event) => setUserName(event.target.value)}
              maxLength={40}
              placeholder="例如：王阿姨、老李…"
              className="w-full rounded-xl border border-black/10 bg-canvas px-4 py-3 text-lg focus:border-companion"
            />
          </div>

          <div className="flex flex-col-reverse sm:flex-row sm:justify-end gap-3 pt-2">
            <button
              type="button"
              onClick={() => void finish(false)}
              disabled={saving}
              className="rounded-xl px-5 py-3 text-lg font-medium text-muted hover:bg-canvas disabled:opacity-50"
            >
              先跳过
            </button>
            <button
              type="submit"
              disabled={saving}
              className="rounded-xl bg-companion px-7 py-3 text-lg font-semibold text-white disabled:opacity-50"
            >
              就这样称呼
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
