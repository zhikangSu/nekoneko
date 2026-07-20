// Mirrors backend app/schemas/profile.py.

export interface ProactiveEffective {
  quiet_hours_start: string;
  quiet_hours_end: string;
  max_checkins_per_day: number;
  same_topic_cooldown_minutes: number;
}

export interface UserProfile {
  user_id: string;
  companion_display_name: string | null;
  user_display_name: string | null;
  onboarding_completed: boolean;
  memory_enabled: boolean;
  proactive_checkin_enabled: boolean;
  // Per-user overrides; null means "follow the backend global default".
  proactive_quiet_hours_start: string | null;
  proactive_quiet_hours_end: string | null;
  proactive_max_checkins_per_day: number | null;
  proactive_same_topic_cooldown_minutes: number | null;
  proactive_effective: ProactiveEffective;
}

export interface ProfileUpdate {
  companion_display_name?: string | null;
  user_display_name?: string | null;
  onboarding_completed?: boolean;
  memory_enabled?: boolean;
  proactive_checkin_enabled?: boolean;
  proactive_quiet_hours_start?: string | null;
  proactive_quiet_hours_end?: string | null;
  proactive_max_checkins_per_day?: number | null;
  proactive_same_topic_cooldown_minutes?: number | null;
}
