import { SensorSimulator } from "@/components/sensors/SensorSimulator";

export default function SensorsPage() {
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold text-ink">关怀模拟</h1>
      <p className="text-muted text-lg">
        用模拟信号看看系统如何把信号转成事件，再决定要不要温和地关心您。这只是演示，
        不接真实设备，也不做医学判断。
      </p>
      <SensorSimulator />
    </div>
  );
}
