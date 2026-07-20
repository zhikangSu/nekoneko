import { notFound } from "next/navigation";

import { EvaluationExportPanel } from "@/components/evaluation/EvaluationExportPanel";

export default function EvaluationPage() {
  if (process.env.NEXT_PUBLIC_SHOW_RESEARCH_UI !== "true") {
    notFound();
  }

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold text-ink">评估导出</h1>
      <p className="text-lg text-muted">
        导出 Trace 摘要和 route/risk 计数；不包含聊天原文。
      </p>
      <EvaluationExportPanel />
    </div>
  );
}
