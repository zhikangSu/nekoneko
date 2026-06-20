// Decode a base64 audio payload (from /api/voice/tts) into a Blob the browser
// can play via an object URL. Browser-only (uses atob).
export function base64ToBlob(base64: string, contentType: string): Blob {
  const binary = atob(base64);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i += 1) {
    bytes[i] = binary.charCodeAt(i);
  }
  return new Blob([bytes], { type: contentType || "audio/wav" });
}
