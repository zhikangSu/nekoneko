"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from "react";

import { getProfile, updateProfile } from "@/lib/apiClient";
import { DEFAULT_USER_ID } from "@/lib/constants";
import type { ProfileUpdate, UserProfile } from "@/types/profile";
import { OnboardingModal } from "./OnboardingModal";

interface ProfileContextValue {
  profile: UserProfile | null;
  loading: boolean;
  // Raw user-chosen name (null when unset); components apply their own fallback.
  companionDisplayName: string | null;
  update: (update: ProfileUpdate) => Promise<void>;
}

const ProfileContext = createContext<ProfileContextValue | null>(null);

export function useProfile(): ProfileContextValue {
  const value = useContext(ProfileContext);
  if (!value) {
    throw new Error("useProfile must be used within a ProfileProvider");
  }
  return value;
}

export function ProfileProvider({ children }: { children: ReactNode }) {
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;
    getProfile(DEFAULT_USER_ID)
      .then((loaded) => {
        if (active) setProfile(loaded);
      })
      .catch(() => {
        // Backend unreachable: stay usable with the neutral fallback; don't
        // force onboarding.
        if (active) setProfile(null);
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, []);

  const update = useCallback(async (changes: ProfileUpdate) => {
    const updated = await updateProfile(DEFAULT_USER_ID, changes);
    setProfile(updated);
  }, []);

  const showOnboarding = !loading && profile !== null && !profile.onboarding_completed;

  return (
    <ProfileContext.Provider
      value={{
        profile,
        loading,
        companionDisplayName: profile?.companion_display_name ?? null,
        update,
      }}
    >
      {children}
      {showOnboarding ? <OnboardingModal /> : null}
    </ProfileContext.Provider>
  );
}
