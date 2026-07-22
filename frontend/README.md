# Frontend — Elderly Companion AI

Next.js (App Router) + TypeScript + TailwindCSS. Slice 1 ships the app shell and
the text Chat page wired to the backend `POST /api/chat`, with reserved slots for
voice, the safety banner, and the Agent Trace panel.

## Setup & run

```bash
cd frontend
npm install
npm run dev        # http://localhost:3000
```

The page calls the backend at `NEXT_PUBLIC_API_BASE_URL` (default
`http://localhost:8000`). Start the backend (see `../backend/README.md`) for live
replies; if it is unreachable, the chat shows a friendly fallback message and
stays usable.

```bash
npm run build      # production build / type-check
npm run lint       # next lint
```

The research-only evaluation export is hidden from the coursework-delivery UI
by default. Set `NEXT_PUBLIC_SHOW_RESEARCH_UI=true` before starting or building
the frontend to restore the evaluation navigation and page for a later study.
The internal demo-video checklist is not part of the product UI.

## What's here (Slice 1)

- `src/app/layout.tsx` — wraps every page in `AppShell` (header shows the
  companion name; neutral fallback **陪伴 AI / AI Companion** until onboarding).
- `src/app/page.tsx`, `src/app/chat/page.tsx` — render the chat experience.
- `src/components/chat/` — `ChatExperience`, `ChatWindow`, `MessageBubble`,
  `SafetyBanner` (slot), `VoiceRecorderButton` / `ReplayButton` (disabled slots),
  mode toggle (陪伴优先 / 助理模式).
- `src/components/traces/AgentTracePanel.tsx` — renders the live trace returned
  by the backend, keeping the Agent / Tool / Guard distinction visible.
- `src/hooks/useChat.ts`, `src/lib/apiClient.ts` — chat state + typed API client.
- `src/types/` — `chat.ts`, `trace.ts` mirror the backend schemas.

## Accessibility (older-adult friendly)

Large base type (~18px+), big touch targets, high-contrast calm palette, visible
focus rings, `Enter` to send / `Shift+Enter` for newline, and a text-first
layout. No youth slang, memes, or playful copy.

## Naming rule

The companion has **no hardcoded fixed name**. The UI reads
`companion_display_name` (from onboarding, #21) and falls back to the neutral
label when unset — never an invented default.

## Not in Slice 1

Onboarding / naming flow (#21), real voice I/O (#4/#23), Memory Center (#10),
Reminders (#11), Sensor Simulator (#12/#22), and the trace history API (#9). The
voice and safety-banner slots are reserved so those land without relayout.
