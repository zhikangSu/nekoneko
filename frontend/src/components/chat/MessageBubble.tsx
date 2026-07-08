import { COMPANION_FALLBACK_NAME_SHORT } from "@/lib/constants";
import type {
  ChatMessage,
  RelationshipRoleId,
  RoleCueMessage,
} from "@/types/chat";

const ROLE_STYLE: Record<RelationshipRoleId, string> = {
  same_age_peer: "border-teal-300 bg-teal-50",
  curious_junior: "border-sky-300 bg-sky-50",
  middle_age_bridge: "border-indigo-300 bg-indigo-50",
  elder_mentor: "border-amber-300 bg-amber-50",
  theme_companion: "border-emerald-300 bg-emerald-50",
  memory_organizer: "border-violet-300 bg-violet-50",
  boundary_guardian: "border-rose-300 bg-rose-50",
  no_ai_role: "border-stone-300 bg-stone-50",
};

export function MessageBubble({
  message,
  companionDisplayName,
}: {
  message: ChatMessage;
  companionDisplayName?: string | null;
}) {
  const isUser = message.role === "user";
  const companionLabel =
    companionDisplayName && companionDisplayName.trim()
      ? companionDisplayName.trim()
      : COMPANION_FALLBACK_NAME_SHORT;
  const roleMessages =
    !isUser && !message.isError ? message.roleMessages ?? [] : [];
  const roleText = roleMessages
    .map((roleMessage) => `${roleMessage.role_label}：${roleMessage.text}`)
    .join("\n")
    .trim();
  const showPrimaryBubble =
    isUser ||
    message.isError ||
    roleMessages.length === 0 ||
    message.text.trim() !== roleText;

  return (
    <div className={isUser ? "flex justify-end" : "flex justify-start"}>
      <div className="max-w-[85%]">
        <div
          className={`mb-1 text-base ${isUser ? "text-right text-muted" : "text-companion"}`}
        >
          {isUser ? "您" : companionLabel}
        </div>
        {roleMessages.length > 0 ? (
          <div className="space-y-2">
            {roleMessages.map((roleMessage, index) => (
              <RoleBubble
                key={`${roleMessage.role_id ?? "role"}-${index}`}
                message={roleMessage}
              />
            ))}
          </div>
        ) : null}
        {showPrimaryBubble ? (
          <div
            className={[
              "rounded-2xl px-5 py-3 text-lg leading-relaxed whitespace-pre-wrap break-words",
              roleMessages.length > 0 ? "mt-2" : "",
              isUser
                ? "bg-user-soft text-ink rounded-tr-sm"
                : message.isError
                  ? "bg-caution-soft text-caution rounded-tl-sm"
                  : "bg-companion-soft text-ink rounded-tl-sm",
            ].join(" ")}
          >
            {message.text}
          </div>
        ) : null}
      </div>
    </div>
  );
}

function RoleBubble({ message }: { message: RoleCueMessage }) {
  const style = message.role_id
    ? ROLE_STYLE[message.role_id] ?? "border-black/10 bg-companion-soft"
    : "border-black/10 bg-companion-soft";

  return (
    <div
      className={[
        "rounded-2xl rounded-tl-sm border-l-4 px-5 py-3 text-lg leading-relaxed text-ink",
        style,
      ].join(" ")}
    >
      <div className="mb-1 text-sm font-semibold text-muted">
        {message.role_label}
      </div>
      <div className="whitespace-pre-wrap break-words">{message.text}</div>
    </div>
  );
}
