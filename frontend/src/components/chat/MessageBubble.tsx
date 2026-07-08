import { COMPANION_FALLBACK_NAME_SHORT } from "@/lib/constants";
import type {
  ChatMessage,
  RelationshipRoleId,
  RoleCueMessage,
} from "@/types/chat";

const ROLE_ACCENT_STYLE: Record<RelationshipRoleId, string> = {
  same_age_peer: "border-teal-300",
  curious_junior: "border-sky-300",
  middle_age_bridge: "border-indigo-300",
  elder_mentor: "border-amber-300",
  theme_companion: "border-emerald-300",
  memory_organizer: "border-violet-300",
  boundary_guardian: "border-rose-300",
  no_ai_role: "border-stone-300",
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
          <SocialCueScene roleMessages={roleMessages} />
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

function SocialCueScene({
  roleMessages,
}: {
  roleMessages: RoleCueMessage[];
}) {
  return (
    <div className="rounded-2xl rounded-tl-sm border border-companion/15 bg-companion-soft px-5 py-4 text-ink">
      <div className="mb-3 flex flex-wrap items-baseline justify-between gap-x-4 gap-y-1">
        <div className="text-base font-semibold text-companion">
          几位陪伴角色先聊两句
        </div>
        <div className="text-sm text-muted">想说就说，不着急</div>
      </div>
      <div className="space-y-3">
        {roleMessages.map((roleMessage, index) => (
          <RoleLine
            key={`${roleMessage.role_id ?? "role"}-${index}`}
            message={roleMessage}
            isInvitation={
              roleMessages.length >= 3 && index === roleMessages.length - 1
            }
          />
        ))}
      </div>
    </div>
  );
}

function RoleLine({
  message,
  isInvitation,
}: {
  message: RoleCueMessage;
  isInvitation: boolean;
}) {
  const accentStyle = message.role_id
    ? ROLE_ACCENT_STYLE[message.role_id] ?? "border-black/10"
    : "border-black/10";

  return (
    <div
      className={[
        "border-l-4 pl-4 text-lg leading-relaxed text-ink",
        isInvitation ? "bg-surface/70 py-3 pr-4" : "py-1",
        isInvitation ? "rounded-xl border-companion" : accentStyle,
      ].join(" ")}
    >
      <div
        className={`mb-1 text-sm font-semibold ${
          isInvitation ? "text-companion" : "text-muted"
        }`}
      >
        {isInvitation ? "也想听您说说" : message.role_label}
      </div>
      <div className="whitespace-pre-wrap break-words">{message.text}</div>
    </div>
  );
}
