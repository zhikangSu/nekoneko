import { ReminderManager } from "@/components/reminders/ReminderManager";

export default function RemindersPage() {
  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-semibold text-ink">提醒</h1>
      <p className="text-muted text-lg">
        吃药、喝水、日程提醒。我只负责按时提醒；用药具体怎么吃，请按医嘱。
      </p>
      <ReminderManager />
    </div>
  );
}
