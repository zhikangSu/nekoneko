// Reserved slot for safety messaging. In Slice 1 it shows a calm, persistent
// note. #8 will drive dynamic high-risk states (e.g. medication / emergency
// templates) into this same slot. Kept gentle, not alarming (AGENTS.md §11).
export function SafetyBanner() {
  return (
    <div
      role="note"
      className="rounded-xl bg-caution-soft text-caution px-4 py-3 text-base leading-relaxed"
    >
      目前只是演示陪伴，不能提供医疗诊断或用药建议，也不会代为拨打急救电话。遇到紧急情况，请联系家人或当地急救服务。
    </div>
  );
}
