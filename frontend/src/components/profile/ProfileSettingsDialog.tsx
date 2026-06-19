"use client";

import { useEffect, useState } from "react";

import { COMPANION_FALLBACK_NAME } from "@/lib/constants";
import { useProfile } from "./ProfileProvider";

// Rename / clear the companion name and toggle basic preferences (#21). The
// fuller Memory Center arrives in #10; this is the minimal settings surface.
export function ProfileSettingsDialog({
  open,
  onClose,
}: {
  open: boolean;
  onClose: () => void;
}) {
  const { profile, update } = useProfile();
  const [companionName, setCompanionName] = useState("");
  const [userName, setUserName] = useState("");
  const [saving, setSaving] = useState(false);

  // Re-sync form when opened or when the profile changes.
  useEffect(() => {
    if (open) {
      setCompanionName(profile?.companion_display_name ?? "");
      setUserName(profile?.user_display_name ?? "");
    }
  }, [open, profile]);

  if (!open) return null;

  async function save() {
    if (saving) return;
    setSaving(true);
    try {
      await update({
        companion_display_name: companionName.trim() || null,
        user_display_name: userName.trim() || null,
      });
      onClose();
    } finally {
      setSaving(false);
    }
  }

  async function clearCompanionName() {
    if (saving) return;
    setSaving(true);
    try {
      await update({ companion_display_name: null });
      setCompanionName("");
    } finally {
      setSaving(false);
    }
  }

  async function toggle(
    field: "memory_enabled" | "proactive_checkin_enabled",
    value: boolean,
  ) {
    await update({ [field]: value });
  }

  return (
    <div
      className="fixed inset-0 z-50 grid place-items-center bg-black/30 px-4"
      role="dialog"
      aria-modal="true"
      aria-labelledby="settings-title"
    >
      <div className="w-full max-w-lg rounded-2xl bg-surface p-7 shadow-xl">
        <h2 id="settings-title" className="text-2xl font-semibold text-ink">
          设置
        </h2>
        <p className="mt-1 text-base text-muted">
          未设置名字时，我会叫作「{COMPANION_FALLBACK_NAME}」。
        </p>

        <div className="mt-5 space-y-4">
          <div>
            <label htmlFor="s-companion" className="block text-lg text-ink mb-1">
              我的称呼
            </label>
            <div className="flex gap-2">
              <input
                id="s-companion"
                value={companionName}
                onChange={(event) => setCompanionName(event.target.value)}
                maxLength={40}
                placeholder={COMPANION_FALLBACK_NAME}
                className="flex-1 rounded-xl border border-black/10 bg-canvas px-4 py-3 text-lg focus:border-companion"
              />
              <button
                type="button"
                onClick={() => void clearCompanionName()}
                disabled={saving || !profile?.companion_display_name}
                className="rounded-xl px-4 py-3 text-base text-caution hover:bg-caution-soft disabled:opacity-40"
              >
                删除名字
              </button>
            </div>
          </div>

          <div>
            <label htmlFor="s-user" className="block text-lg text-ink mb-1">
              您的称呼
            </label>
            <input
              id="s-user"
              value={userName}
              onChange={(event) => setUserName(event.target.value)}
              maxLength={40}
              placeholder="（可不填）"
              className="w-full rounded-xl border border-black/10 bg-canvas px-4 py-3 text-lg focus:border-companion"
            />
          </div>

          <Toggle
            label="记住我说过的偏好"
            checked={profile?.memory_enabled ?? true}
            onChange={(value) => void toggle("memory_enabled", value)}
          />
          <Toggle
            label="允许主动关怀问候"
            checked={profile?.proactive_checkin_enabled ?? true}
            onChange={(value) => void toggle("proactive_checkin_enabled", value)}
          />
        </div>

        <div className="mt-6 flex flex-col-reverse sm:flex-row sm:justify-end gap-3">
          <button
            type="button"
            onClick={onClose}
            disabled={saving}
            className="rounded-xl px-5 py-3 text-lg font-medium text-muted hover:bg-canvas disabled:opacity-50"
          >
            关闭
          </button>
          <button
            type="button"
            onClick={() => void save()}
            disabled={saving}
            className="rounded-xl bg-companion px-7 py-3 text-lg font-semibold text-white disabled:opacity-50"
          >
            保存
          </button>
        </div>
      </div>
    </div>
  );
}

function Toggle({
  label,
  checked,
  onChange,
}: {
  label: string;
  checked: boolean;
  onChange: (value: boolean) => void;
}) {
  return (
    <label className="flex items-center justify-between gap-3 py-1">
      <span className="text-lg text-ink">{label}</span>
      <input
        type="checkbox"
        checked={checked}
        onChange={(event) => onChange(event.target.checked)}
        className="h-6 w-6 accent-companion"
      />
    </label>
  );
}
