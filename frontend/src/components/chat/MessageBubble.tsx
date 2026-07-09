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

const ROLE_LABELS: Record<RelationshipRoleId, string> = {
  same_age_peer: "同龄共鸣者",
  curious_junior: "晚辈好奇者",
  middle_age_bridge: "中年传承者",
  elder_mentor: "长辈引导者",
  theme_companion: "主题陪伴者",
  memory_organizer: "回忆整理者",
  boundary_guardian: "边界守护者",
  no_ai_role: "不需要 AI 角色",
};

const GENERAL_NO_ROLE_LABEL = "百事通";

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
  const speakerLabel = isUser
    ? "您"
    : message.isError
      ? companionLabel
      : getCompanionSpeakerLabel(message, roleMessages, companionLabel);
  const roleText = roleMessages
    .map((roleMessage) => `${roleMessage.role_label}：${roleMessage.text}`)
    .join("\n")
    .trim();
  const showPrimaryBubble =
    isUser ||
    message.isError ||
    roleMessages.length === 0 ||
    message.text.trim() !== roleText;

  if (!isUser && !message.isError && roleMessages.length > 0) {
    return (
      <div className="space-y-3">
        {roleMessages.map((roleMessage, index) => (
          <RoleMessageBubble
            key={`${roleMessage.role_id ?? "role"}-${index}`}
            message={roleMessage}
          />
        ))}
      </div>
    );
  }

  return (
    <div className={isUser ? "flex justify-end" : "flex justify-start"}>
      <div className="max-w-[85%]">
        <div
          className={`mb-1 text-base ${isUser ? "text-right text-muted" : "text-companion"}`}
        >
          {speakerLabel}
        </div>
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

function getCompanionSpeakerLabel(
  message: ChatMessage,
  roleMessages: RoleCueMessage[],
  companionLabel: string,
) {
  if (roleMessages.length > 0) {
    const roleLabels = uniqueLabels(
      roleMessages.map((roleMessage) => roleMessage.role_label),
    );
    return roleLabels.length > 0 ? roleLabels.join("、") : "关系角色";
  }

  if (usesNoRoleResponder(message)) {
    return GENERAL_NO_ROLE_LABEL;
  }

  const manualRoleLabels = selectedTalkRoleLabels(message);
  if (manualRoleLabels.length > 0) {
    return manualRoleLabels.join("、");
  }

  return companionLabel;
}

function uniqueLabels(labels: string[]) {
  return labels.filter((label, index) => label && labels.indexOf(label) === index);
}

function selectedTalkRoleLabels(message: ChatMessage) {
  const traceRole = message.trace?.research_trace?.role;
  const ids = [
    ...(message.requestedRoleIds ?? []),
    ...(traceRole?.selected_roles ?? []),
    ...(traceRole?.requested_role_ids ?? []),
  ];
  return uniqueLabels(
    ids
      .filter(isRelationshipRoleId)
      .filter((id) => id !== "no_ai_role")
      .map((id) => ROLE_LABELS[id]),
  );
}

function isRelationshipRoleId(value: string): value is RelationshipRoleId {
  return value in ROLE_LABELS;
}

function usesNoRoleResponder(message: ChatMessage) {
  const traceRole = message.trace?.research_trace?.role;
  return (
    message.requestedRoleIds?.includes("no_ai_role") ||
    traceRole?.selected_roles?.includes("no_ai_role") ||
    traceRole?.requested_role_ids?.includes("no_ai_role") ||
    traceRole?.primary_role === "no_ai_role"
  );
}

function RoleMessageBubble({
  message,
}: {
  message: RoleCueMessage;
}) {
  const accentStyle = message.role_id
    ? ROLE_ACCENT_STYLE[message.role_id] ?? "border-black/10"
    : "border-black/10";

  return (
    <div className="flex justify-start">
      <div className="max-w-[85%]">
        <div className="mb-1 text-base font-semibold text-companion">
          {message.role_label}
        </div>
        <div
          className={[
            "rounded-2xl rounded-tl-sm border-l-4 bg-companion-soft px-5 py-3 text-lg leading-relaxed text-ink whitespace-pre-wrap break-words",
            accentStyle,
          ].join(" ")}
        >
          {message.text}
        </div>
      </div>
    </div>
  );
}
