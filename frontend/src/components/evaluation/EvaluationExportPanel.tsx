"use client";

import { useCallback, useEffect, useState } from "react";

import { getEvaluationCsv, getEvaluationExport } from "@/lib/apiClient";
import { DEFAULT_USER_ID } from "@/lib/constants";
import type { EvaluationExport } from "@/types/evaluation";

const ROUTE_LABELS: Record<string, string> = {
  companion_chat: "陪伴对话",
  safety_response: "安全回复",
  emergency_mock: "紧急边界演示",
  proactive_checkin: "主动关怀",
  reminder_management: "提醒管理",
  memory_management: "记忆管理",
  retrieval_supported_response: "受控查询",
  relationship_cueing: "关系话题引导",
};

const DEMO_CHECKLIST = [
  "完成一次文字或语音陪伴对话",
  "展示用户可命名的陪伴 AI 设置",
  "新增、确认或删除一条提醒",
  "展示 Memory Center 的查看与删除",
  "运行一次关怀模拟并打开 Trace",
  "演示天气/时间敏感问题的受控查询",
  "演示健康或用药高风险问题的安全回复",
  "导出评估 JSON 或 CSV 作为报告素材",
];

export function EvaluationExportPanel() {
  const [summary, setSummary] = useState<EvaluationExport | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);
  const [downloading, setDownloading] = useState(false);

  const refresh = useCallback(async () => {
    try {
      setSummary(await getEvaluationExport(DEFAULT_USER_ID));
      setError(false);
    } catch {
      setError(true);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  async function downloadJson() {
    if (!summary) return;
    const blob = new Blob([JSON.stringify(summary, null, 2)], {
      type: "application/json",
    });
    downloadBlob(blob, `qaq-evaluation-${DEFAULT_USER_ID}.json`);
  }

  async function downloadCsv() {
    setDownloading(true);
    try {
      downloadBlob(
        await getEvaluationCsv(DEFAULT_USER_ID),
        `qaq-evaluation-${DEFAULT_USER_ID}.csv`,
      );
    } finally {
      setDownloading(false);
    }
  }

  if (loading) return <p className="text-lg text-muted">正在加载…</p>;
  if (error || summary === null) {
    return (
      <p className="text-lg text-caution">
        连不上后台服务，请确认后端已启动（http://localhost:8000）。
      </p>
    );
  }

  return (
    <div className="space-y-6">
      <div className="grid gap-3 md:grid-cols-4">
        <Metric label="Trace turns" value={summary.trace_count} />
        <Metric label="Safety critic" value={summary.safety_critic_turns} />
        <Metric label="Retrieval" value={summary.retrieval_turns} />
        <Metric label="Routes" value={Object.keys(summary.route_counts).length} />
      </div>

      <div className="flex flex-wrap gap-3">
        <button
          type="button"
          onClick={() => void downloadJson()}
          className="rounded-lg bg-companion px-5 py-3 text-lg font-semibold text-white"
        >
          下载 JSON
        </button>
        <button
          type="button"
          onClick={() => void downloadCsv()}
          disabled={downloading}
          className="rounded-lg bg-user px-5 py-3 text-lg font-semibold text-white disabled:opacity-50"
        >
          下载 CSV
        </button>
        <button
          type="button"
          onClick={() => void refresh()}
          className="rounded-lg px-5 py-3 text-lg font-medium text-companion hover:bg-companion-soft"
        >
          刷新
        </button>
      </div>

      <div className="grid gap-5 lg:grid-cols-[1fr_1fr]">
        <section className="rounded-lg border border-black/10 bg-surface p-5">
          <h2 className="text-xl font-semibold text-ink">Route 汇总</h2>
          <CountList counts={summary.route_counts} labels={ROUTE_LABELS} />
        </section>

        <section className="rounded-lg border border-black/10 bg-surface p-5">
          <h2 className="text-xl font-semibold text-ink">Risk 汇总</h2>
          <CountList counts={summary.risk_counts} />
        </section>
      </div>

      <section className="rounded-lg border border-black/10 bg-surface p-5">
        <div className="flex flex-wrap items-end justify-between gap-2">
          <h2 className="text-xl font-semibold text-ink">Demo video checklist</h2>
          <span className="text-sm text-muted">
            导出于 {formatDateTime(summary.exported_at)}
          </span>
        </div>
        <ul className="mt-4 grid gap-3 md:grid-cols-2">
          {DEMO_CHECKLIST.map((item) => (
            <li key={item} className="flex gap-3 text-base text-ink">
              <span
                aria-hidden
                className="mt-1 h-5 w-5 shrink-0 rounded border border-companion"
              />
              <span>{item}</span>
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}

function Metric({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-lg border border-black/10 bg-surface p-4">
      <p className="text-sm text-muted">{label}</p>
      <p className="mt-2 text-3xl font-semibold tabular-nums text-companion">
        {value}
      </p>
    </div>
  );
}

function CountList({
  counts,
  labels = {},
}: {
  counts: Record<string, number>;
  labels?: Record<string, string>;
}) {
  const entries = Object.entries(counts);
  if (entries.length === 0) {
    return <p className="mt-3 text-base text-muted">暂无数据。</p>;
  }
  return (
    <ul className="mt-3 space-y-2">
      {entries.map(([key, value]) => (
        <li
          key={key}
          className="flex items-center justify-between gap-3 border-b border-black/5 pb-2 last:border-0 last:pb-0"
        >
          <span className="text-base text-ink">{labels[key] ?? key}</span>
          <span className="text-base font-semibold tabular-nums text-companion">
            {value}
          </span>
        </li>
      ))}
    </ul>
  );
}

function downloadBlob(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  link.click();
  URL.revokeObjectURL(url);
}

function formatDateTime(value: string) {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString("zh-CN", {
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
  });
}
