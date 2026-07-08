# Issue 75: Short-Term Conversation History

GitHub issue: https://github.com/Freyalilith/QAQ/issues/75

## User-Reported Gap

The demo can show multiple chat turns in the UI, but `/api/chat` does not yet pass
recent user/assistant turns into the LLM. Follow-up questions on the same topic can
therefore lose the immediately preceding context.

## Confirmed Current Behavior

- `frontend/src/hooks/useChat.ts` sends only the current `message`.
- `backend/app/schemas/chat.py` has no request field for history, session, or thread id.
- `backend/app/api/routes/chat.py` builds `GraphState` from the current message and profile.
- `backend/app/services/xiaomimimo_llm_provider.py` sends only `system` plus current `user`.
- `TraceStore` persists trace history and `MemoryTool` handles long-term memory, but neither
  currently provides a short-term conversation window to the LLM.

## Acceptance Criteria

- Add short-term conversation/session history for `/api/chat`, scoped by `user_id` or session id.
- Include the last 6-10 user/assistant messages when calling the real LLM provider.
- Keep safety routing, controlled retrieval, and long-term memory behavior unchanged.
- Do not automatically save sensitive short-term content as durable memory.
- Add offline regression coverage proving a follow-up turn can use the previous turn.
- Surface trace metadata that short-term history was used without exposing full sensitive chat text.

## Handoff

Completed:
- Created GitHub issue #75 with reproduction notes and acceptance criteria.
- Added this repository note so the backlog item is discoverable from git history.

Tested:
- Inspected the current request schema, frontend send path, graph construction, LLM provider payload,
  trace store, and memory tool behavior.

Not done:
- The short-term history implementation itself is not included in this note.

Risks / questions:
- Choose whether conversation history should be keyed only by `user_id` or by an explicit session id.
- Keep visible trace privacy-preserving: count/used flag is safer than full message dumps.

Next recommended step:
- Implement a small conversation history store and pass a bounded recent window into the LLM provider.
