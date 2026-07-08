"use client";

import { useCallback, useEffect, useRef, useState } from "react";

import { synthesizeSpeech, transcribeAudio } from "@/lib/apiClient";
import { base64ToBlob } from "@/lib/audio";
import { WavRecorder, isRecordingSupported } from "@/lib/wavRecorder";

export type RecorderState = "idle" | "recording" | "transcribing";
export type TTSSpeed = 0.85 | 1 | 1.15;

export interface PendingTranscript {
  text: string;
  confidence: number;
}

export interface VoiceControls {
  // Output (TTS)
  autoSpeak: boolean;
  setAutoSpeak: (on: boolean) => void;
  ttsSpeed: TTSSpeed;
  setTtsSpeed: (speed: TTSSpeed) => void;
  isSpeaking: boolean;
  isMockVoice: boolean;
  speak: (text: string) => void; // play / replay a reply on demand
  stopSpeaking: () => void;
  // Input (record → ASR)
  recordingSupported: boolean;
  recorderState: RecorderState;
  startRecording: () => void;
  stopRecording: () => void;
  pendingTranscript: PendingTranscript | null;
  submitPendingTranscript: () => void;
  editPendingTranscript: (text: string) => void;
  dismissPendingTranscript: () => void;
  // Gentle status, e.g. "我刚才没听清…". Null when there is nothing to say.
  hint: string | null;
  clearHint: () => void;
}

const DIDNT_CATCH = "我刚才没听清，您可以再说一次，或直接打字告诉我。";
const NO_MIC = "没能打开麦克风，请检查权限，或直接打字和我说话。";
const ASR_FAILED = "语音识别暂时没成功，您可以直接打字和我说话。";
// Auto-stop a forgotten recording so the uploaded WAV can't grow without bound.
const MAX_RECORDING_MS = 60_000;
const LOW_CONFIDENCE_THRESHOLD = 0.65;

// Orchestrates the voice loop: press to record → ASR → feed the transcript into
// chat; auto-read or replay companion replies with TTS. Recording produces WAV
// (the real ASR provider needs it, #23; the mock accepts it too). Voice is always
// an enhancement — every failure path leaves the text chat fully usable.
export function useVoice({
  onTranscript,
}: {
  onTranscript: (text: string) => void;
}): VoiceControls {
  const [recordingSupported, setRecordingSupported] = useState(false);
  const [recorderState, setRecorderState] = useState<RecorderState>("idle");
  const [hint, setHint] = useState<string | null>(null);
  const [autoSpeak, setAutoSpeak] = useState(false);
  const [ttsSpeed, setTtsSpeed] = useState<TTSSpeed>(1);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [isMockVoice, setIsMockVoice] = useState(false);
  const [pendingTranscript, setPendingTranscript] =
    useState<PendingTranscript | null>(null);

  const recorderRef = useRef<WavRecorder | null>(null);
  const maxTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const stopRecordingRef = useRef<() => void>(() => undefined);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const lastUrlRef = useRef<string | null>(null);
  const lastTextRef = useRef<string | null>(null);

  const clearMaxTimer = useCallback(() => {
    if (maxTimerRef.current) {
      clearTimeout(maxTimerRef.current);
      maxTimerRef.current = null;
    }
  }, []);

  // Keep the latest onTranscript without re-creating the recorder callbacks.
  const onTranscriptRef = useRef(onTranscript);
  useEffect(() => {
    onTranscriptRef.current = onTranscript;
  });

  useEffect(() => {
    setRecordingSupported(isRecordingSupported());
  }, []);

  // Release audio + mic + timer when the chat unmounts.
  useEffect(() => {
    return () => {
      if (maxTimerRef.current) clearTimeout(maxTimerRef.current);
      recorderRef.current?.dispose();
      audioRef.current?.pause();
      if (lastUrlRef.current) URL.revokeObjectURL(lastUrlRef.current);
    };
  }, []);

  const stopSpeaking = useCallback(() => {
    audioRef.current?.pause();
    setIsSpeaking(false);
  }, []);

  const speak = useCallback(async (text: string) => {
    const clean = text.trim();
    if (!clean) return;
    try {
      // Replay the same reply from the cached clip; otherwise synthesize.
      let url = lastUrlRef.current;
      if (!url || lastTextRef.current !== clean) {
        const result = await synthesizeSpeech(clean);
        setIsMockVoice(result.is_mock);
        const blob = base64ToBlob(result.audio_base64, result.content_type);
        if (lastUrlRef.current) URL.revokeObjectURL(lastUrlRef.current);
        url = URL.createObjectURL(blob);
        lastUrlRef.current = url;
        lastTextRef.current = clean;
      }

      let audio = audioRef.current;
      if (!audio) {
        audio = new Audio();
        audioRef.current = audio;
      }
      audio.pause();
      audio.src = url;
      audio.currentTime = 0;
      audio.playbackRate = ttsSpeed;
      audio.onended = () => setIsSpeaking(false);
      audio.onerror = () => setIsSpeaking(false);
      setIsSpeaking(true);
      await audio.play();
    } catch {
      // Autoplay blocked / network hiccup — non-fatal, the text reply is shown.
      setIsSpeaking(false);
    }
  }, [ttsSpeed]);

  const startRecording = useCallback(async () => {
    if (!isRecordingSupported()) {
      setHint("这台设备暂时用不了麦克风，您可以直接打字和我说话。");
      return;
    }
    setHint(null);
    const recorder = new WavRecorder();
    try {
      await recorder.start();
      recorderRef.current = recorder;
      setRecorderState("recording");
      // Safety cap: auto-stop if the user forgets to.
      maxTimerRef.current = setTimeout(
        () => stopRecordingRef.current(),
        MAX_RECORDING_MS,
      );
    } catch {
      recorder.dispose();
      setRecorderState("idle");
      setHint(NO_MIC);
    }
  }, []);

  const stopRecording = useCallback(async () => {
    clearMaxTimer();
    const recorder = recorderRef.current;
    if (!recorder) return;
    recorderRef.current = null;
    setRecorderState("transcribing");
    let blob: Blob;
    try {
      blob = await recorder.stop();
    } catch {
      setRecorderState("idle");
      setHint(ASR_FAILED);
      return;
    }
    try {
      const result = await transcribeAudio(blob);
      if (result.ok && result.transcript.trim()) {
        const transcript = result.transcript.trim();
        setHint(null);
        if (result.confidence < LOW_CONFIDENCE_THRESHOLD) {
          setPendingTranscript({
            text: transcript,
            confidence: result.confidence,
          });
        } else {
          onTranscriptRef.current(transcript);
        }
      } else {
        setHint(DIDNT_CATCH);
      }
    } catch {
      setHint(ASR_FAILED);
    } finally {
      setRecorderState("idle");
    }
  }, [clearMaxTimer]);

  // Let the max-duration timer call the current stopRecording without making it
  // a dependency of startRecording.
  useEffect(() => {
    stopRecordingRef.current = stopRecording;
  });

  const clearHint = useCallback(() => setHint(null), []);
  const submitPendingTranscript = useCallback(() => {
    const text = pendingTranscript?.text.trim();
    if (!text) return;
    setPendingTranscript(null);
    onTranscriptRef.current(text);
  }, [pendingTranscript]);
  const editPendingTranscript = useCallback((text: string) => {
    setPendingTranscript((current) =>
      current ? { ...current, text } : current,
    );
  }, []);
  const dismissPendingTranscript = useCallback(
    () => setPendingTranscript(null),
    [],
  );

  return {
    autoSpeak,
    setAutoSpeak,
    ttsSpeed,
    setTtsSpeed,
    isSpeaking,
    isMockVoice,
    speak,
    stopSpeaking,
    recordingSupported,
    recorderState,
    startRecording,
    stopRecording,
    pendingTranscript,
    submitPendingTranscript,
    editPendingTranscript,
    dismissPendingTranscript,
    hint,
    clearHint,
  };
}
