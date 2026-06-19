// Mirrors backend app/schemas/profile.py.

export interface UserProfile {
  user_id: string;
  companion_display_name: string | null;
  user_display_name: string | null;
  onboarding_completed: boolean;
  memory_enabled: boolean;
  proactive_checkin_enabled: boolean;
}

export interface ProfileUpdate {
  companion_display_name?: string | null;
  user_display_name?: string | null;
  onboarding_completed?: boolean;
  memory_enabled?: boolean;
  proactive_checkin_enabled?: boolean;
}
