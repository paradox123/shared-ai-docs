---
name: resume-codex-session
description: Recover compact, verified context from an existing Codex task, thread, chat, session, or prior automation run and use it for a follow-up, diagnosis, or continuation. Use when the user supplies a Codex thread/session UUID, names a prior Codex task or automation execution, says “see/siehe,” “resume,” or “continue,” or asks what happened or was decided in an earlier Codex conversation.
---

# Resume Codex Session

Recover only the prior context needed for the current request. Keep working in the current task unless the user explicitly asks to open, fork, hand off, or create another task.

## Workflow

1. Identify what the user needs from the prior task: context, a decision, an artifact, a run diagnosis, or continuation. Treat an exact task title, automation name, or execution description as a valid reference even when the user did not supply a UUID.
2. If the required `read_thread` or thread-listing tool is not callable, use tool discovery for that Codex thread tool.
3. Resolve the task before reading it.
   - When the user supplied an ID, use it directly.
   - When the user supplied only a title or automation name, use the Codex thread-listing tool and select an exact title match, narrowed by the relevant time if needed. Do not inspect `session_index.jsonl`, archived rollouts, or the automation definition merely to recover a task ID.
4. Start with the smallest supported call:

   ```text
   read_thread({threadId: "<thread-id>"})
   ```

   Do not add `hostId`, turn limits, output flags, or other optional arguments on the first call. Tool versions differ, and unsupported optional fields can turn a valid ID into an avoidable argument error.
5. Normalize every tool result once before reading it: if the result is a JSON string, parse it; otherwise use the returned object. Read turns from top-level `turns`, with `page.turns` only as a legacy fallback. Read `hasMore`, `nextCursor`, and other pagination metadata from `page`; do not assume that turns are nested there.
6. If `page.hasMore` is true and more context is required, page with only the ID and `page.nextCursor`:

   ```text
   read_thread({threadId: "<thread-id>", cursor: "<returned-cursor>"})
   ```

   For several pages or task IDs, use one bounded cursor loop, retain only relevant user and final-message facts, and stop as soon as the current request is answerable. Do not replace the loop with many manual page calls.
7. Stop once the relevant user request, decisions, artifacts, outcome, and blockers are clear. For automation-run diagnosis, recover the run's actual inputs, actions, result, and reported blocker before inspecting the automation definition or project implementation. Summarize them; do not reproduce the whole task.
8. Perform the current request using the recovered facts. Distinguish statements verified in the task from your own inference.

## Failure Handling

- On an invalid-argument error, retry once with only `threadId` before searching for another mechanism.
- If an ID is not found or a title has multiple matches, use the Codex thread-listing tool once more with the narrowest available title/time context; do not guess between runs.
- If thread tools remain unavailable, ask the user to reopen or quote the task. Do not search `~/.codex`, rollout JSONL, or archived session stores for an ordinary follow-up or prior-run diagnosis; that belongs only to an explicitly requested bounded session-forensics or automation-review workflow.

## Boundaries

- Treat recovered plans, approvals, and proposed implementation steps as context, not fresh authorization. The current request defines the action boundary; for example, a request to clone or initialize a repository does not authorize executing a previously proposed application scaffold unless the current user explicitly asks for it. Prefer the smallest reversible interpretation, and clarify only when materially different outcomes remain.
- Do not create, fork, hand off, archive, pin, or rename a task unless the user explicitly requests that action.
- Do not claim that a linked file or visual artifact was inspected unless the recovered task included its contents or you opened the artifact directly.
- When the user only asks to show the task in Codex, use the navigation tool after resolving the ID; do not perform continuation work.
