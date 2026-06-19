import { MemoryCenter } from "@/components/memory/MemoryCenter";

export default function MemoryPage() {
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold text-ink">记忆中心</h1>
      <p className="text-muted text-lg">
        这里是我记住的、关于您的事。您随时可以删除，也可以暂停我继续记忆。
      </p>
      <MemoryCenter />
    </div>
  );
}
