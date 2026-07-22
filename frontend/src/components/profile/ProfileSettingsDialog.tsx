"use client";

import { useEffect, useRef, useState } from "react";

import { COMPANION_FALLBACK_NAME } from "@/lib/constants";
import { PROACTIVE_TOPIC_BANK } from "@/lib/proactiveTopics";
import type { ProfileUpdate, UserProfile } from "@/types/profile";
import { useProfile } from "./ProfileProvider";

interface ProactiveFormValues {
  quietStart: string;
  quietEnd: string;
  maxCheckins: string;
  cooldownMinutes: string;
}

const BUILT_IN_PROACTIVE_VALUES: ProactiveFormValues = {
  quietStart: "22:00",
  quietEnd: "07:00",
  maxCheckins: "3",
  cooldownMinutes: "120",
};

function proactiveFormValues(profile: UserProfile | null): ProactiveFormValues {
  const effective = profile?.proactive_effective;
  return {
    quietStart:
      profile?.proactive_quiet_hours_start ??
      effective?.quiet_hours_start ??
      BUILT_IN_PROACTIVE_VALUES.quietStart,
    quietEnd:
      profile?.proactive_quiet_hours_end ??
      effective?.quiet_hours_end ??
      BUILT_IN_PROACTIVE_VALUES.quietEnd,
    maxCheckins: String(
      profile?.proactive_max_checkins_per_day ??
        effective?.max_checkins_per_day ??
        BUILT_IN_PROACTIVE_VALUES.maxCheckins,
    ),
    cooldownMinutes: String(
      profile?.proactive_same_topic_cooldown_minutes ??
        effective?.same_topic_cooldown_minutes ??
        BUILT_IN_PROACTIVE_VALUES.cooldownMinutes,
    ),
  };
}

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
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const initialProactiveRef = useRef<ProactiveFormValues>(
    BUILT_IN_PROACTIVE_VALUES,
  );
  const formInitializedRef = useRef(false);

  // Initialize once per open cycle. Immediate toggle saves update ``profile``;
  // they must not wipe other unsaved text/limit edits in this dialog.
  useEffect(() => {
    if (!open) {
      formInitializedRef.current = false;
      return;
    }
    if (formInitializedRef.current || !profile) return;
    const proactive = proactiveFormValues(profile);
    setCompanionName(profile.companion_display_name ?? "");
    setUserName(profile.user_display_name ?? "");
    setQuietStart(proactive.quietStart);
    setQuietEnd(proactive.quietEnd);
    setMaxCheckins(proactive.maxCheckins);
    setCooldownMinutes(proactive.cooldownMinutes);
    initialProactiveRef.current = proactive;
    formInitializedRef.current = true;
    setErrorMessage(null);
  }, [open, profile]);

  if (!open) return null;

  async function save() {
    if (saving) return;
    setSaving(true);
    setErrorMessage(null);
    try {
      const changes: ProfileUpdate = {
        companion_display_name: companionName.trim() || null,
        user_display_name: userName.trim() || null,
      };
      const initial = initialProactiveRef.current;
      if (quietStart !== initial.quietStart) {
        changes.proactive_quiet_hours_start = quietStart.trim() || null;
      }
      if (quietEnd !== initial.quietEnd) {
        changes.proactive_quiet_hours_end = quietEnd.trim() || null;
      }
      if (maxCheckins !== initial.maxCheckins) {
        changes.proactive_max_checkins_per_day = parseOptionalInt(
          maxCheckins,
          0,
          6,
          "每日最多问候",
        );
      }
      if (cooldownMinutes !== initial.cooldownMinutes) {
        changes.proactive_same_topic_cooldown_minutes = parseOptionalInt(
          cooldownMinutes,
          0,
          720,
          "同类话题冷却",
        );
      }
      await update(changes);
      onClose();
    } catch (error) {
      setErrorMessage(
        error instanceof Error && error.message.startsWith("请输入")
          ? error.message
          : "保存没成功，请检查填写内容和后台连接后再试一次。",
      );
    } finally {
      setSaving(false);
    }
  }

  async function clearCompanionName() {
    if (saving) return;
    setSaving(true);
    setErrorMessage(null);
    try {
      await update({ companion_display_name: null });
      setCompanionName("");
    } catch {
      setErrorMessage("删除名字没成功，请确认后台连接后再试一次。");
    } finally {
      setSaving(false);
    }
  }

  async function toggle(
    field: "memory_enabled" | "proactive_checkin_enabled",
    value: boolean,
  ) {
    setErrorMessage(null);
    try {
      await update({ [field]: value });
    } catch {
      setErrorMessage("设置没保存成功，请确认后台连接后再试一次。");
    }
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
            <p className="mt-1 text-sm leading-6 text-muted">
              当前显示的是实际生效值；只会保存您改过的项目。清空某一项可恢复全局默认。
            </p>
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

        {errorMessage ? (
          <p role="alert" className="mt-4 text-base text-caution">
            {errorMessage}
          </p>
        ) : null}

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

function parseOptionalInt(
  value: string,
  min: number,
  max: number,
  label: string,
): number | null {
  const normalized = value.trim();
  if (!normalized) return null;
  const parsed = Number(normalized);
  if (!Number.isInteger(parsed) || parsed < min || parsed > max) {
    throw new Error(`请输入 ${min}–${max} 之间的${label}数值。`);
  }
  return parsed;
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
