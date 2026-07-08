import { API_BASE_URL } from "./constants";
import type {
  ASRResponse,
  ChatRequest,
  ChatResponse,
  TTSResponse,
} from "@/types/chat";
import type { CaregiverSummary } from "@/types/caregiver";
import type {
  CardStatus,
  MemoryCard,
  MemoryCardAction,
  MemoryCardList,
  MemoryCategory,
  MemoryEntry,
  MemoryView,
} from "@/types/memory";
import type { ProfileUpdate, UserProfile } from "@/types/profile";
import type { Reminder, ReminderCreate } from "@/types/reminder";
import type {
  ApplyPresetResponse,
  SensorPreset,
  StateEventType,
} from "@/types/sensor";
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

// --- Caregiver mock dashboard (#79) -----------------------------------------

export async function getCaregiverSummary(
  userId: string,
): Promise<CaregiverSummary> {
  const params = new URLSearchParams({ user_id: userId });
  return jsonOrThrow(
    await fetch(`${API_BASE_URL}/api/caregiver/summary?${params.toString()}`),
    "Get caregiver summary",
  );
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

// --- Memory Cards (#54) -----------------------------------------------------

// Propose a draft card from an utterance. The backend returns 201 with the
// card, or 204 (no body) when no candidate is found — we map 204 to null.
export async function draftMemoryCard(
  userId: string,
  text: string,
  sourceTurnId?: string,
): Promise<MemoryCard | null> {
  const response = await fetch(
    `${API_BASE_URL}/api/memory-cards/${userId}/draft`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(
        sourceTurnId ? { text, source_turn_id: sourceTurnId } : { text },
      ),
    },
  );
  if (response.status === 204) return null;
  return jsonOrThrow(response, "Draft memory card");
}

export async function listMemoryCards(
  userId: string,
  status?: CardStatus,
): Promise<MemoryCardList> {
  const query = status ? `?status=${encodeURIComponent(status)}` : "";
  return jsonOrThrow(
    await fetch(`${API_BASE_URL}/api/memory-cards/${userId}${query}`),
    "List memory cards",
  );
}

export async function actOnMemoryCard(
  userId: string,
  cardId: string,
  action: MemoryCardAction,
  editedSummary?: string,
): Promise<MemoryCard> {
  return jsonOrThrow(
    await fetch(`${API_BASE_URL}/api/memory-cards/${userId}/${cardId}/action`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(
        editedSummary !== undefined
          ? { action, edited_summary: editedSummary }
          : { action },
      ),
    }),
    "Act on memory card",
  );
}

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

// --- Sensors / proactive care (#22, #12) ------------------------------------

export async function getSensorPresets(): Promise<SensorPreset[]> {
  return jsonOrThrow(
    await fetch(`${API_BASE_URL}/api/sensors/presets`),
    "Get presets",
  );
}

export async function applyPreset(
  userId: string,
  presetId: string,
): Promise<ApplyPresetResponse> {
  return jsonOrThrow(
    await fetch(`${API_BASE_URL}/api/sensors/apply-preset`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_id: userId, preset_id: presetId }),
    }),
    "Apply preset",
  );
}

export async function refuseCare(
  userId: string,
  eventType: StateEventType,
): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/sensors/refuse`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_id: userId, event_type: eventType }),
  });
  if (!response.ok) {
    throw new Error(`Refuse care failed with status ${response.status}`);
  }
}

// --- Voice I/O (#4) ----------------------------------------------------------

// The recorded clip is sent as the raw request body (the backend reads bytes
// directly — no multipart). An empty/too-short clip comes back with ok=false.
export async function transcribeAudio(audio: Blob): Promise<ASRResponse> {
  return jsonOrThrow(
    await fetch(`${API_BASE_URL}/api/voice/asr`, {
      method: "POST",
      headers: audio.type ? { "Content-Type": audio.type } : undefined,
      body: audio,
    }),
    "Transcribe audio",
  );
}

export async function synthesizeSpeech(
  text: string,
  voice?: string,
): Promise<TTSResponse> {
  return jsonOrThrow(
    await fetch(`${API_BASE_URL}/api/voice/tts`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(voice ? { text, voice } : { text }),
    }),
    "Synthesize speech",
  );
}
