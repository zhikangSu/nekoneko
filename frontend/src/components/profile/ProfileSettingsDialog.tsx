"use client";

import { useEffect, useState } from "react";

import { COMPANION_FALLBACK_NAME } from "@/lib/constants";
import { PROACTIVE_TOPIC_BANK } from "@/lib/proactiveTopics";
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
  const [quietStart, setQuietStart] = useState("22:00");
  const [quietEnd, setQuietEnd] = useState("07:00");
  const [maxCheckins, setMaxCheckins] = useState("3");
  const [cooldownMinutes, setCooldownMinutes] = useState("120");
  const [saving, setSaving] = useState(false);

  // Re-sync form when opened or when the profile changes.
  useEffect(() => {
    if (open) {
      setCompanionName(profile?.companion_display_name ?? "");
      setUserName(profile?.user_display_name ?? "");
      setQuietStart(profile?.proactive_quiet_hours_start ?? "22:00");
      setQuietEnd(profile?.proactive_quiet_hours_end ?? "07:00");
      setMaxCheckins(String(profile?.proactive_max_checkins_per_day ?? 3));
      setCooldownMinutes(
        String(profile?.proactive_same_topic_cooldown_minutes ?? 120),
      );
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
        proactive_quiet_hours_start: quietStart,
        proactive_quiet_hours_end: quietEnd,
        proactive_max_checkins_per_day: clampInt(maxCheckins, 0, 6, 3),
        proactive_same_topic_cooldown_minutes: clampInt(
          cooldownMinutes,
          0,
          720,
          120,
        ),
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
      <div className="max-h-[calc(100vh-2rem)] w-full max-w-2xl overflow-y-auto rounded-2xl bg-surface p-7 shadow-xl">
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

          <div className="border-t border-black/10 pt-4">
            <h3 className="text-lg font-semibold text-ink">主动关怀规则</h3>
            <div className="mt-3 grid gap-3 sm:grid-cols-2">
              <label className="block">
                <span className="mb-1 block text-base text-muted">安静时段开始</span>
                <input
                  type="time"
                  value={quietStart}
                  onChange={(event) => setQuietStart(event.target.value)}
                  className="w-full rounded-xl border border-black/10 bg-canvas px-4 py-3 text-lg focus:border-companion"
                />
              </label>
              <label className="block">
                <span className="mb-1 block text-base text-muted">安静时段结束</span>
                <input
                  type="time"
                  value={quietEnd}
                  onChange={(event) => setQuietEnd(event.target.value)}
                  className="w-full rounded-xl border border-black/10 bg-canvas px-4 py-3 text-lg focus:border-companion"
                />
              </label>
              <label className="block">
                <span className="mb-1 block text-base text-muted">每日最多问候</span>
                <input
                  type="number"
                  min={0}
                  max={6}
                  value={maxCheckins}
                  onChange={(event) => setMaxCheckins(event.target.value)}
                  className="w-full rounded-xl border border-black/10 bg-canvas px-4 py-3 text-lg focus:border-companion"
                />
              </label>
              <label className="block">
                <span className="mb-1 block text-base text-muted">
                  同类话题冷却（分钟）
                </span>
                <input
                  type="number"
                  min={0}
                  max={720}
                  step={15}
                  value={cooldownMinutes}
                  onChange={(event) => setCooldownMinutes(event.target.value)}
                  className="w-full rounded-xl border border-black/10 bg-canvas px-4 py-3 text-lg focus:border-companion"
                />
              </label>
            </div>
          </div>

          <div className="border-t border-black/10 pt-4">
            <h3 className="text-lg font-semibold text-ink">低风险话题库</h3>
            <ul className="mt-3 space-y-3">
              {PROACTIVE_TOPIC_BANK.map((topic) => (
                <li key={topic.id} className="border-l-4 border-companion/45 pl-3">
                  <p className="text-base font-semibold text-ink">{topic.label}</p>
                  <p className="text-sm leading-6 text-muted">{topic.cue}</p>
                </li>
              ))}
            </ul>
          </div>
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

function clampInt(
  value: string,
  min: number,
  max: number,
  fallback: number,
): number {
  const parsed = Number.parseInt(value, 10);
  if (!Number.isFinite(parsed)) return fallback;
  return Math.min(max, Math.max(min, parsed));
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
