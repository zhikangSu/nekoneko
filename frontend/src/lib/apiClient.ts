import { API_BASE_URL } from "./constants";
import type { ChatRequest, ChatResponse } from "@/types/chat";
import type { MemoryCategory, MemoryEntry, MemoryView } from "@/types/memory";
import type { ProfileUpdate, UserProfile } from "@/types/profile";
import type { Reminder, ReminderCreate } from "@/types/reminder";
import type { TraceRecord, TraceSummary } from "@/types/trace";

async function jsonOrThrow<T>(response: Response, what: string): Promise<T> {
  if (!response.ok) {
    throw new Error(`${what} failed with status ${response.status}`);
  }
  return (await response.json()) as T;
}

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

// --- Memory (#10) -----------------------------------------------------------

export async function getMemory(userId: string): Promise<MemoryView> {
  return jsonOrThrow(
    await fetch(`${API_BASE_URL}/api/memory/${userId}`),
    "Get memory",
  );
}

export async function addMemory(
  userId: string,
  category: MemoryCategory,
  content: string,
): Promise<MemoryEntry> {
  return jsonOrThrow(
    await fetch(`${API_BASE_URL}/api/memory/${userId}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ category, content }),
    }),
    "Add memory",
  );
}

export async function deleteMemory(
  userId: string,
  memoryId: string,
): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/memory/${userId}/${memoryId}`, {
    method: "DELETE",
  });
  if (!response.ok) {
    throw new Error(`Delete memory failed with status ${response.status}`);
  }
}

export async function setMemoryPaused(
  userId: string,
  paused: boolean,
): Promise<MemorySettingsResponse> {
  return jsonOrThrow(
    await fetch(`${API_BASE_URL}/api/memory/${userId}/settings`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ extraction_paused: paused }),
    }),
    "Update memory settings",
  );
}

type MemorySettingsResponse = { extraction_paused: boolean };

// --- Reminders (#11) --------------------------------------------------------

export async function getReminders(userId: string): Promise<Reminder[]> {
  return jsonOrThrow(
    await fetch(`${API_BASE_URL}/api/reminders/${userId}`),
    "Get reminders",
  );
}

export async function addReminder(
  userId: string,
  reminder: ReminderCreate,
): Promise<Reminder> {
  return jsonOrThrow(
    await fetch(`${API_BASE_URL}/api/reminders/${userId}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(reminder),
    }),
    "Add reminder",
  );
}

export async function deleteReminder(
  userId: string,
  reminderId: string,
): Promise<void> {
  const response = await fetch(
    `${API_BASE_URL}/api/reminders/${userId}/${reminderId}`,
    { method: "DELETE" },
  );
  if (!response.ok) {
    throw new Error(`Delete reminder failed with status ${response.status}`);
  }
}

export async function confirmReminder(
  userId: string,
  reminderId: string,
): Promise<Reminder> {
  return jsonOrThrow(
    await fetch(`${API_BASE_URL}/api/reminders/${userId}/${reminderId}/confirm`, {
      method: "POST",
    }),
    "Confirm reminder",
  );
}

export async function triggerReminder(
  userId: string,
  reminderId: string,
): Promise<{ reminder: Reminder; message: string }> {
  return jsonOrThrow(
    await fetch(`${API_BASE_URL}/api/reminders/${userId}/${reminderId}/trigger`, {
      method: "POST",
    }),
    "Trigger reminder",
  );
}
