"use client";

// Voice output (#4): read the latest companion reply aloud, and replay it on
// demand. Disabled until there is a reply to read. In DEMO_MODE the audio is a
// placeholder tone (real speech arrives with #23), so we say so quietly.
export function ReplayButton({
  text,
  isSpeaking,
  isMockVoice,
  onPlay,
  onStop,
}: {
  text: string | null;
  isSpeaking: boolean;
  isMockVoice: boolean;
  onPlay: () => void;
  onStop: () => void;
}) {
  const disabled = !text;

  return (
    <div className="flex items-center gap-3">
      <button
        type="button"
        onClick={isSpeaking ? onStop : onPlay}
        disabled={disabled}
        title={disabled ? "还没有可朗读的回复" : isSpeaking ? "停止朗读" : "请再说一遍"}
        className="inline-flex items-center gap-2 rounded-xl px-3 py-2 text-base text-companion disabled:text-muted disabled:opacity-60 disabled:cursor-not-allowed"
      >
        <span aria-hidden>{isSpeaking ? "⏸" : "🔊"}</span>
        {isSpeaking ? "停止朗读" : "请再说一遍"}
      </button>
      {isMockVoice && !disabled ? (
        <span className="text-sm text-muted">（演示用模拟语音）</span>
      ) : null}
    </div>
  );
}
