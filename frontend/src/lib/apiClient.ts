import { API_BASE_URL } from "./constants";
import type { ChatRequest, ChatResponse } from "@/types/chat";
import type { ProfileUpdate, UserProfile } from "@/types/profile";
import type { TraceRecord, TraceSummary } from "@/types/trace";

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

export async function getTrace(turnId: string): Promise<TraceRecord> {
  const response = await fetch(`${API_BASE_URL}/api/traces/${turnId}`);
  if (!response.ok) {
    throw new Error(`Get trace failed with status ${response.status}`);
  }
  return (await response.json()) as TraceRecord;
}

export async function listTraces(
  userId: string,
  limit = 10,
): Promise<TraceSummary[]> {
  const params = new URLSearchParams({ user_id: userId, limit: String(limit) });
  const response = await fetch(`${API_BASE_URL}/api/traces?${params.toString()}`);
  if (!response.ok) {
    throw new Error(`List traces failed with status ${response.status}`);
  }
  return (await response.json()) as TraceSummary[];
}
