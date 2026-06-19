"use client";

import { useCallback, useEffect, useState } from "react";

import { applyPreset, getSensorPresets, refuseCare } from "@/lib/apiClient";
import { DEFAULT_USER_ID } from "@/lib/constants";
import type {
  ApplyPresetResponse,
  GuardianDecisionType,
  SensorPreset,
} from "@/types/sensor";

const DECISION_LABELS: Record<GuardianDecisionType, string> = {
  check_in: "主动问候",
  defer: "暂不打扰",
  silent_log: "静默记录",
  safety_escalation: "升级关怀",
};
const DECISION_STYLES: Record<GuardianDecisionType, string> = {
  check_in: "bg-companion-soft text-companion",
  defer: "bg-black/5 text-muted",
  silent_log: "bg-black/5 text-muted",
  safety_escalation: "bg-caution-soft text-caution",
};

export function SensorSimulator() {
  const [presets, setPresets] = useState<SensorPreset[]>([]);
  const [result, setResult] = useState<ApplyPresetResponse | null>(null);
  const [busy, setBusy] = useState(false);
  const [refused, setRefused] = useState(false);
  const [error, setError] = useState(false);

  const loadPresets = useCallback(async () => {
    try {
      setPresets(await getSensorPresets());
      setError(false);
    } catch {
      setError(true);
    }
  }, []);

  useEffect(() => {
    void loadPresets();
  }, [loadPresets]);

  async function handleApply(presetId: string) {
    setBusy(true);
    setRefused(false);
    try {
      setResult(await applyPreset(DEFAULT_USER_ID, presetId));
      setError(false);
    } catch {
      setError(true);
    } finally {
      setBusy(false);
    }
  }

  async function handleRefuse() {
    if (!result) return;
    await refuseCare(DEFAULT_USER_ID, result.state_event.event_type);
    setRefused(true);
  }

  if (error && presets.length === 0) {
    return (
      <p className="text-caution text-lg">
        连不上后台服务，请确认后端已启动（http://localhost:8000）。
      </p>
    );
  }

  const decision = result?.guardian_decision.decision;
  const canRefuse = decision === "check_in" || decision === "safety_escalation";

  return (
    <div className="space-y-6">
      <section>
        <h2 className="text-lg font-semibold text-ink mb-2">模拟信号</h2>
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {presets.map((preset) => (
            <button
              key={preset.id}
              type="button"
              disabled={busy}
              onClick={() => void handleApply(preset.id)}
              className="rounded-2xl bg-surface border border-black/5 px-5 py-4 text-left hover:border-companion disabled:opacity-50"
            >
              <div className="text-lg font-semibold text-ink">{preset.label}</div>
              <div className="text-base text-muted">{preset.description}</div>
            </button>
          ))}
        </div>
      </section>

      {result ? (
        <section className="rounded-2xl bg-surface border border-black/5 p-5 space-y-4">
          <div>
            <h3 className="text-base font-semibold text-muted uppercase tracking-wide">
              StateEvent（由 SensorAdapter 生成）
            </h3>
            <div className="mt-1 text-lg text-ink font-semibold">
              {result.state_event.event_type}
            </div>
            <dl className="mt-1 grid grid-cols-[auto_1fr] gap-x-3 gap-y-1 text-base">
              <dt className="text-muted">severity</dt>
              <dd className="text-ink">{result.state_event.severity}</dd>
              <dt className="text-muted">confidence</dt>
              <dd className="text-ink">{result.state_event.confidence}</dd>
              <dt className="text-muted">medical_claim</dt>
              <dd className="text-ink">
                {result.state_event.medical_claim_allowed ? "allowed" : "false（不做医学解释）"}
              </dd>
            </dl>
            <p className="mt-1 text-base text-muted">{result.state_event.rationale}</p>
          </div>

          <div>
            <h3 className="text-base font-semibold text-muted uppercase tracking-wide">
              GuardianAgent 决策
            </h3>
            <div className="mt-1 flex items-center gap-2">
              <span
                className={`rounded-md px-2 py-0.5 text-base font-medium ${
                  decision ? DECISION_STYLES[decision] : ""
                }`}
              >
                {decision ? DECISION_LABELS[decision] : ""}
              </span>
              {result.guardian_decision.cooldown_applied ? (
                <span className="text-base text-muted">
                  冷却 {result.guardian_decision.cooldown_minutes} 分钟
                </span>
              ) : null}
            </div>
            <p className="mt-1 text-base text-muted">
              克制考量：{result.guardian_decision.restraint_critique}
            </p>
          </div>

          {result.response_text ? (
            <div className="rounded-xl bg-companion-soft text-ink px-4 py-3 text-lg">
              🌿 {result.response_text}
            </div>
          ) : (
            <p className="text-muted text-base">本次 Guardian 选择不主动开口。</p>
          )}

          {canRefuse ? (
            refused ? (
              <p className="text-base text-companion">
                已记录您的拒绝，同类关怀会进入冷却，暂时不再打扰。
              </p>
            ) : (
              <button
                type="button"
                onClick={() => void handleRefuse()}
                className="rounded-xl px-5 py-2.5 text-base text-caution hover:bg-caution-soft"
              >
                我现在不想被打扰
              </button>
            )
          ) : null}
        </section>
      ) : (
        <p className="text-muted text-lg">
          点一个上面的预设，看看 SensorAdapter 会生成什么事件、Guardian 会不会主动关怀。
        </p>
      )}
    </div>
  );
}
