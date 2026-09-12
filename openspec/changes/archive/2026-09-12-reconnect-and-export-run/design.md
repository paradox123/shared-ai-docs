## Context

Ticket 09 continues completed Tickets 03/04. PostgreSQL owns canonical positions;
framework runtime history remains supplemental. The public acceptance seams are
HTTP/CLI read-back and separate replacement worker processes.

## Decisions

- Cursor pages return `nextAfter` (last delivered position) separately from the
  snapshot high-water `lastPosition` and `hasMore`. SSE uses the same committed
  history, `id: position`, and Last-Event-ID. Clients acknowledge only processed
  events and reconnect strictly after that position; replay from an older cursor
  intentionally repeats unacknowledged delivery. Each page/tail poll revalidates
  current provider authorization. No successful terminal output is needed.
- Artifact bytes live beneath an explicit local `WPCP_ARTIFACT_ROOT` (required in the API, worker and restore process). SHA-256 names bind sanitized bytes, never
  raw input. Writes are atomic, immutable, and precede transactional references.
  Orphaned safe bytes after a crash are acceptable; a missing reference target is
  reported as unavailable and is never silently accepted as valid evidence.
- Redact decoded JSON/text recursively before persistence, including encoded
  artifact content. Opaque binary input containing a controlled canary is withheld
  with policy metadata rather than rewritten into a corrupt binary. Controlled
  canaries are a deterministic pilot policy, not general PII detection.
- Large adapter observations are stored as JSON artifacts and replayed from that
  same sanitized original. Event payloads and projections retain references.
- A dossier is a versioned ZIP with canonical JSON history/projection, manifest,
  SHA-256 integrity records, artifact bytes and explicit provenance/correlations.
  Export takes a coherent database snapshot. Missing/corrupt bytes remain manifest
  entries with visible reasons. Restored dossiers are historical, read-only views;
  they cannot revive leases, execute workers or qualify a head. Current repository
  access still gates every read. Restore is an explicit local service command into
  empty components and cannot overwrite a live run.
- Qualification eligibility is an artifact-integrity prerequisite only; passing
  it does not qualify a head or implement later review/qualification tickets.

## Verification

Use disposable PostgreSQL and artifact roots, controlled external provider inputs,
SIGKILL/replacement processes, paged HTTP/SSE and CLI, and a fresh restore API.
Compare public canonical history/projection/artifact hashes and scan only the
disposable pilot storage/logs for the complete controlled-canary inventory.
