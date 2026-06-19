import type { TraceSummary } from "@/types/trace";

const ROUTE_LABELS: Record<string, string> = {
  companion_chat: "陪伴",
  safety_response: "安全",
  emergency_mock: "紧急(演示)",
  proactive_checkin: "主动关怀",
  reminder_management: "提醒",
  memory_management: "记忆",
  retrieval_supported_response: "联网查询",
};

const RISK_STYLES: Record<string, string> = {
  low: "bg-black/5 text-muted",
  medium: "bg-caution-soft text-caution",
  high: "bg-caution-soft text-caution",
  crisis: "bg-caution text-white",
};

function formatTime(iso: string): string {
  // created_at is ISO-8601; show HH:MM, fall back to the raw string.
  const match = iso.match(/T(\d{2}:\d{2})/);
  return match ? match[1] : iso;
}

export function TraceHistory({
  rows,
  activeTurnId,
  onSelect,
}: {
  rows: TraceSummary[];
  activeTurnId?: string;
  onSelect: (turnId: string) => void;
}) {
  if (rows.length === 0) return null;

  return (
    <div>
      <h3 className="text-base font-semibold text-muted uppercase tracking-wide">
        历史记录
      </h3>
      <ul className="mt-1 space-y-1">
        {rows.map((row) => {
          const active = row.turn_id === activeTurnId;
          return (
            <li key={row.turn_id}>
              <button
                type="button"
                onClick={() => onSelect(row.turn_id)}
                aria-current={active}
                className={`w-full flex items-center justify-between gap-2 rounded-lg px-3 py-2 text-left text-base ${
                  active ? "bg-companion-soft" : "hover:bg-canvas"
                }`}
              >
                <span className="text-muted tabular-nums">
                  {formatTime(row.created_at)}
                </span>
                <span className="flex-1 text-ink truncate">
                  {ROUTE_LABELS[row.route] ?? row.route}
                </span>
                <span
                  className={`rounded-md px-2 py-0.5 text-sm ${
                    RISK_STYLES[row.risk_level] ?? RISK_STYLES.low
                  }`}
                >
                  {row.risk_level}
                </span>
              </button>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
