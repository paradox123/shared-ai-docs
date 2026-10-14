# QMD MCP in the audit chat — 2026-10-14

This is a bounded verification summary of actual returned tool contents, not a copy of the audit history.

- Chat: `Main: Audit-Tickets parallel starten`, ID `01a10252-83fc-7473-8068-e5e28b400a16`.
- Authorization: Daniel explicitly selected “MCP-Testauftrag senden” after being told that the chat was idle and the message would start a new read-only turn.
- Test turn: `01a1393e-ecd7-7191-bc75-3a9576bc339c`, started 2026-10-14 09:09:47 Europe/Berlin, completed 09:11:01 without error; the chat returned to idle.
- Tool discovery returned QMD `get`, `multi_get`, `query` and `status`.

| Actual MCP call | Observed result |
|---|---|
| `status`, `exec-5b2655c1-6118-451f-bfcb-f1302db1ba6b` | `isError:false`; `totalDocuments:2599`, `needsEmbedding:0`, `hasVectorIndex:true`; 26 collections. |
| `query`, `exec-98854662-3b6b-4608-b13b-f11d807a62a6` | `searches:[{type:"lex",query:"QMD"}]`, `collections:["danielsvault-rag"]`, `limit:2`, `rerank:false`; `isError:false`; returned `#6b1baa` README and `#6c3295` deployment document. |
| `get`, `exec-ed80d653-d447-46a8-b56b-db25b99d4665` | `file:"#6b1baa"`, `fromLine:1`, `maxLines:8`, `lineNumbers:true`; `isError:false`; Markdown resource `qmd://danielsvault-rag/readme.md`, first line `# DanielsVault QMD Runtime`, eight lines returned. |

The chat API confirmed completed call metadata. Actual result contents were checked against the exact test-turn recorder outputs in the known rollout: `call_49c11cb5d97e4b9597cdb7bd8a8c9f1b` at 07:10:25.995Z for status/query, and `call_665858916d574fe7aaf452a0bc9765a6` at 07:10:51.688Z for get. No broad audit-history copy was needed.

No active audit turn was interrupted. The test performed no audit-file edits, index maintenance, permission changes, restart or forced reload. It verifies this named local chat; it does not establish availability on arbitrary remote/cloud hosts.
