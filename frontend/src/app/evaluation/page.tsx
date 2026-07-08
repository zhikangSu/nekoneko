import { EvaluationExportPanel } from "@/components/evaluation/EvaluationExportPanel";

export default function EvaluationPage() {
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold text-ink">评估导出</h1>
      <p className="text-lg text-muted">
        导出 Trace 摘要、route/risk 计数和 demo video 检查项；不包含聊天原文。
      </p>
      <EvaluationExportPanel />
    </div>
  );
}
