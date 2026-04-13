# Initialize

## Goal
Bootstrap every new NCG agent session with deterministic project context when running inside `/Users/dh/Documents/Dev/NCG/ncg-backend`.

## Steps
1. Determine repository root from current working context.
2. Continue only if root is `/Users/dh/Documents/Dev/NCG/ncg-backend`; otherwise return a short skip note (`ContextBootstrap not applicable for this repository`).
3. Collect baseline docs in order:
    - `README.md` at repo root (if present)
    - `backend/sources/README.md` (if present)
    - `backend/sources/AGENT.md` (if present)
    - `backend/sources/SERVICES_INVENTORY.md` (if present)
    - `backend/sources/tests/README.md` (if present)
    - targeted external docs anchors:
      - `/Users/dh/Documents/DanielsVault/ncg/ncg-docs/docs/Ops/README.md`
      - `/Users/dh/Documents/DanielsVault/ncg/ncg-docs/docs/Ops/Environments/Development/Dev-Environment.md`
      - `/Users/dh/Documents/DanielsVault/ncg/ncg-docs/docs/Ops/Services/GitLab-CI-CD.md`
      - `/Users/dh/Documents/DanielsVault/ncg/ncg-docs/docs/Ops/Services/Service-Dependency-Graph.md`
      - `/Users/dh/Documents/DanielsVault/ncg/ncg-docs/docs/Ops/Security/Secrets-Management.md`
      - `/Users/dh/Documents/DanielsVault/ncg/ncg-docs/docs/Ops/Security/Certificates.md`
4. Collect repository structure anchors:
    - top-level folders relevant to runtime/services/shared libraries
    - solution/workspace manifests and project files
5. Collect runnable commands from concrete sources (in priority order):
    - documented commands in README/AGENT/docs
    - scripts/task runners/manifests in repository
    - CI/pipeline definitions if needed
6. Extract architecture and operational context:
    - service boundaries and responsibilities
    - important dependencies/infrastructure touchpoints
    - environment/setup constraints mentioned in ops guides
    - include known local intent shortcuts for this repo (e.g. `watch my next build` => local watcher command flow)
7. Handle missing documentation explicitly:
    - if README/`backend/sources/AGENT.md` are missing or sparse, rely on code/config/docs inference
    - mark uncertain items as assumptions and lower confidence
8. Return output in strict order (Output Contract).
9. Write SessionId at file bottom if not already present; use the startup resume SessionId.

## Output Contract
Return headings in this exact order:
1) Repository
2) Structure Snapshot
3) Build/Test/Run Commands
4) Architecture Snapshot
5) Ops Guide Anchors
6) Gaps & Assumptions
7) Suggested First Actions
8) Confidence

## Output Format
- Repository:
   - Root: `/Users/dh/Documents/Dev/NCG/ncg-backend`
   - Mode: `auto-start` | `manual-refresh`
- Structure Snapshot:
   - {key folder/service anchor}
- Build/Test/Run Commands:
   - {command} — Source: {path/doc}
- Architecture Snapshot:
   - {service or subsystem} -> {responsibility}
- Ops Guide Anchors:
   - {doc path} — {why relevant}
- Gaps & Assumptions:
   - {missing info or inferred assumption}
- Suggested First Actions:
   - {1-3 startup actions for this session}
- Confidence:
   - Structure: {high|medium|low}
   - Commands: {high|medium|low}
   - Architecture: {high|medium|low}
   - Ops: {high|medium|low}

## Verification Matrix
- Applicability:
   - Session in `/Users/dh/Documents/Dev/NCG/ncg-backend` => workflow executes.
   - Session outside target repo => returns non-failing skip note.
- Missing-doc fallback:
   - Missing `README.md` and/or `backend/sources/AGENT.md` does not block output.
   - Commands/architecture are inferred from manifests/config/docs with reduced confidence.
- Determinism:
   - Headings always follow Output Contract order.
   - Same repository state yields semantically equivalent context summary.
