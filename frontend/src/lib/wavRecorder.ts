"use client";

// Record microphone audio as 16 kHz mono 16-bit WAV — the format the real ASR
// provider (#23) accepts. The browser's MediaRecorder only emits webm/opus, so
// we capture raw PCM via the Web Audio API and encode the WAV ourselves.
// ScriptProcessorNode is deprecated but works in every current browser and needs
// no separate worklet module, which keeps this self-contained for the demo.

const TARGET_SAMPLE_RATE = 16000;

type AudioContextCtor = typeof AudioContext;

function audioContextCtor(): AudioContextCtor | null {
  if (typeof window === "undefined") return null;
  return (
    window.AudioContext ||
    (window as unknown as { webkitAudioContext?: AudioContextCtor })
      .webkitAudioContext ||
    null
  );
}

// True only where we can both capture a mic and run the Web Audio graph.
export function isRecordingSupported(): boolean {
  return (
    typeof navigator !== "undefined" &&
    !!navigator.mediaDevices &&
    typeof navigator.mediaDevices.getUserMedia === "function" &&
    audioContextCtor() !== null
  );
}

export class WavRecorder {
  private context: AudioContext | null = null;
  private stream: MediaStream | null = null;
  private source: MediaStreamAudioSourceNode | null = null;
  private processor: ScriptProcessorNode | null = null;
  private chunks: Float32Array[] = [];
  private inputSampleRate = TARGET_SAMPLE_RATE;

  async start(): Promise<void> {
    const Ctor = audioContextCtor();
    if (!Ctor) throw new Error("Web Audio API unavailable");
    this.stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    // Ask for 16 kHz directly; some browsers ignore it, so we still resample.
    try {
      this.context = new Ctor({ sampleRate: TARGET_SAMPLE_RATE });
    } catch {
      this.context = new Ctor();
    }
    this.inputSampleRate = this.context.sampleRate;
    this.source = this.context.createMediaStreamSource(this.stream);
    this.processor = this.context.createScriptProcessor(4096, 1, 1);
    this.chunks = [];
    this.processor.onaudioprocess = (event) => {
      // Copy: the input buffer is reused across callbacks.
      this.chunks.push(new Float32Array(event.inputBuffer.getChannelData(0)));
    };
    this.source.connect(this.processor);
    // A ScriptProcessorNode only runs while connected to a destination; we never
    // write its output buffer, so nothing is played back (no echo/feedback).
    this.processor.connect(this.context.destination);
  }

  async stop(): Promise<Blob> {
    const samples = flatten(this.chunks);
    const pcm = downsample(samples, this.inputSampleRate, TARGET_SAMPLE_RATE);
    this.dispose();
    return new Blob([encodeWav(pcm, TARGET_SAMPLE_RATE)], { type: "audio/wav" });
  }

  dispose(): void {
    this.processor?.disconnect();
    this.source?.disconnect();
    this.stream?.getTracks().forEach((track) => track.stop());
    this.context?.close().catch(() => undefined);
    this.context = null;
    this.stream = null;
    this.source = null;
    this.processor = null;
    this.chunks = [];
  }
}

function flatten(chunks: Float32Array[]): Float32Array {
  let length = 0;
  for (const chunk of chunks) length += chunk.length;
  const out = new Float32Array(length);
  let offset = 0;
  for (const chunk of chunks) {
    out.set(chunk, offset);
    offset += chunk.length;
  }
  return out;
}

// Linear-interpolation resample down to the target rate (good enough for speech).
function downsample(
  samples: Float32Array,
  inRate: number,
  outRate: number,
): Float32Array {
  if (outRate >= inRate || samples.length === 0) return samples;
  const ratio = inRate / outRate;
  const outLength = Math.floor(samples.length / ratio);
  const out = new Float32Array(outLength);
  for (let i = 0; i < outLength; i += 1) {
    const pos = i * ratio;
    const idx = Math.floor(pos);
    const a = samples[idx] ?? 0;
    const b = samples[idx + 1] ?? a;
    out[i] = a + (b - a) * (pos - idx);
  }
  return out;
}

// Float32 [-1, 1] mono → 16-bit PCM WAV (44-byte header + samples).
function encodeWav(samples: Float32Array, sampleRate: number): ArrayBuffer {
  const buffer = new ArrayBuffer(44 + samples.length * 2);
  const view = new DataView(buffer);
  const writeString = (offset: number, text: string) => {
    for (let i = 0; i < text.length; i += 1) {
      view.setUint8(offset + i, text.charCodeAt(i));
    }
  };
  writeString(0, "RIFF");
  view.setUint32(4, 36 + samples.length * 2, true);
  writeString(8, "WAVE");
  writeString(12, "fmt ");
  view.setUint32(16, 16, true); // PCM header size
  view.setUint16(20, 1, true); // PCM format
  view.setUint16(22, 1, true); // mono
  view.setUint32(24, sampleRate, true);
  view.setUint32(28, sampleRate * 2, true); // byte rate = rate * blockAlign
  view.setUint16(32, 2, true); // block align = channels * bytesPerSample
  view.setUint16(34, 16, true); // bits per sample
  writeString(36, "data");
  view.setUint32(40, samples.length * 2, true);
  let offset = 44;
  for (let i = 0; i < samples.length; i += 1) {
    const clamped = Math.max(-1, Math.min(1, samples[i]));
    view.setInt16(offset, clamped < 0 ? clamped * 0x8000 : clamped * 0x7fff, true);
    offset += 2;
  }
  return buffer;
}
