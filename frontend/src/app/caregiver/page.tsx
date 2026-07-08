import { CaregiverDashboard } from "@/components/caregiver/CaregiverDashboard";

export default function CaregiverPage() {
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold text-ink">照护摘要</h1>
      <p className="text-lg text-muted">
        展示提醒完成、主动关怀和安全事件的摘要；不显示完整聊天记录。
      </p>
      <CaregiverDashboard />
    </div>
  );
}
