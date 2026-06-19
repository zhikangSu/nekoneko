import { API_BASE_URL } from "./constants";
import type { ChatRequest, ChatResponse } from "@/types/chat";
import type { ProfileUpdate, UserProfile } from "@/types/profile";

export async function sendChat(request: ChatRequest): Promise<ChatResponse> {
  const response = await fetch(`${API_BASE_URL}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    throw new Error(`Chat request failed with status ${response.status}`);
  }

  return (await response.json()) as ChatResponse;
}

export async function getProfile(userId: string): Promise<UserProfile> {
  const response = await fetch(`${API_BASE_URL}/api/users/${userId}/profile`);
  if (!response.ok) {
    throw new Error(`Get profile failed with status ${response.status}`);
  }
  return (await response.json()) as UserProfile;
}

export async function updateProfile(
  userId: string,
  update: ProfileUpdate,
): Promise<UserProfile> {
  const response = await fetch(`${API_BASE_URL}/api/users/${userId}/profile`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(update),
  });
  if (!response.ok) {
    throw new Error(`Update profile failed with status ${response.status}`);
  }
  return (await response.json()) as UserProfile;
}
