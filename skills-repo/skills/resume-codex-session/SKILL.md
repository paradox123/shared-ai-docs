---
name: resume-codex-session
description: Recover compact, verified context from an existing Codex task, thread, chat, or session and use it for a follow-up or continuation. Use when the user supplies a Codex thread/session UUID, says “see/siehe,” “resume,” or “continue” a prior Codex task, or asks what happened or was decided in an earlier Codex conversation.
---

# Resume Codex Session

Recover only the prior context needed for the current request. Keep working in the current task unless the user explicitly asks to open, fork, hand off, or create another task.

## Workflow

1. Identify the referenced task ID and what the user needs from it: context, a decision, an artifact, or continuation.
2. If `read_thread` is not callable, use tool discovery for the Codex thread-reading tool.
3. Start with the smallest supported call:

   ```text
   read_thread({threadId: "<thread-id>"})
   ```

   Do not add `hostId`, turn limits, output flags, or other optional arguments on the first call. Tool versions differ, and unsupported optional fields can turn a valid ID into an avoidable argument error.
4. Normalize every tool result once before reading it: if the result is a JSON string, parse it; otherwise use the returned object. Read turns from top-level `turns`, with `page.turns` only as a legacy fallback. Read `hasMore`, `nextCursor`, and other pagination metadata from `page`; do not assume that turns are nested there.
5. If `page.hasMore` is true and more context is required, page with only the ID and `page.nextCursor`:

   ```text
   read_thread({threadId: "<thread-id>", cursor: "<returned-cursor>"})
   ```

   For several pages or task IDs, use one bounded cursor loop, retain only relevant user and final-message facts, and stop as soon as the current request is answerable. Do not replace the loop with many manual page calls.
6. Stop once the relevant user request, decisions, artifacts, outcome, and blockers are clear. Summarize them; do not reproduce the whole task.
7. Perform the current request using the recovered facts. Distinguish statements verified in the task from your own inference.

## Failure Handling

- On an invalid-argument error, retry once with only `threadId` before searching for another mechanism.
- If the ID is not found, use the Codex thread-listing tool to resolve an exact ID or title match.
- If thread tools remain unavailable, ask the user to reopen or quote the task. Do not search `~/.codex`, rollout JSONL, or archived session stores for an ordinary follow-up; that belongs to session-log forensics or automation review.

## Boundaries

- Treat recovered plans, approvals, and proposed implementation steps as context, not fresh authorization. The current request defines the action boundary; for example, a request to clone or initialize a repository does not authorize executing a previously proposed application scaffold unless the current user explicitly asks for it. Prefer the smallest reversible interpretation, and clarify only when materially different outcomes remain.
- Do not create, fork, hand off, archive, pin, or rename a task unless the user explicitly requests that action.
- Do not claim that a linked file or visual artifact was inspected unless the recovered task included its contents or you opened the artifact directly.
- When the user only asks to show the task in Codex, use the navigation tool after resolving the ID; do not perform continuation work.
