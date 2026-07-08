// Mirrors backend app/schemas/profile.py.

export interface UserProfile {
  user_id: string;
  companion_display_name: string | null;
  user_display_name: string | null;
  onboarding_completed: boolean;
  memory_enabled: boolean;
  proactive_checkin_enabled: boolean;
  proactive_quiet_hours_start: string;
  proactive_quiet_hours_end: string;
  proactive_max_checkins_per_day: number;
  proactive_same_topic_cooldown_minutes: number;
}

export interface ProfileUpdate {
  companion_display_name?: string | null;
  user_display_name?: string | null;
  onboarding_completed?: boolean;
  memory_enabled?: boolean;
  proactive_checkin_enabled?: boolean;
  proactive_quiet_hours_start?: string;
  proactive_quiet_hours_end?: string;
  proactive_max_checkins_per_day?: number;
  proactive_same_topic_cooldown_minutes?: number;
}
