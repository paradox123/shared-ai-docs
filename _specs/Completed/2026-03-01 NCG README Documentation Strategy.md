# Iteration 1

## Summary

Define and prioritize README documentation strategy for NCG backend repository to improve onboarding, agent context bootstrapping, and development workflow. Currently only 3 of 83 directories have READMEs, making the codebase difficult to navigate for both humans and agents.

## Context

### Current State
- **Repository:** `/Users/dh/Documents/Dev/NCG/ncg-backend`
- **Documentation vault:** `/Users/dh/Documents/DanielsVault/ncg`
- **Ops guides:** `/Users/dh/Documents/DanielsVault/ncg/ncg-docs/docs/Ops/Guides`
- **Existing READMEs:**
  - `backend/sources/README.md` (538 lines, comprehensive - build commands, architecture, services inventory)
  - `backend/sources/NCG.NuGetServer/README.md`
  - `backend/sources/secrets/README.md`
- **Missing:** 81/83 service and test directories have no documentation
- **ContextBootstrap skill:** Recently updated to auto-load NCG context at startup, but relies on documentation being present

### Architecture Overview
- .NET 8 microservices monorepo (59 projects)
- Ocelot API Gateway + IdentityServer4 authentication
- MariaDB 10.3 with EF Core 8
- Docker/Podman deployment
- Services: Business logic services + Proxy services + Catalog services + Platform shared components

## Requirements

### R1 – Repository Root README
**Priority:** Critical
**Location:** `/Users/dh/Documents/Dev/NCG/ncg-backend/README.md`
**Purpose:** First-contact orientation for developers and agents

**Content:**
- Project mission statement and high-level architecture
- Quick start guide (get running in 5 minutes)
- Repository structure map
- Links to detailed documentation (sources/README.md, documentation vault)
- Development workflow and contribution guidelines
- Technology stack summary

**Acceptance Criteria:**
- A new developer can clone and run the stack within 10 minutes following only this README
- Agent startup via ContextBootstrap skill can extract: project purpose, main commands, where to find detailed docs

### R2 – AGENT.md for AI Context
**Priority:** High (directly supports ContextBootstrap skill)
**Location:** `/Users/dh/Documents/Dev/NCG/ncg-backend/AGENT.md`
**Purpose:** Structured machine-readable context for agent sessions

**Content:**
- Service inventory with responsibility matrix (service name → domain responsibility)
- Common development task recipes (run one service, debug, test, deploy)
- Architecture decision records (ADRs) or links to them
- Quick reference: "Where to find X" routing table
- Known conventions (naming, folder structure, testing patterns)
- Integration points (external APIs, message queues, shared infrastructure)

**Format:**
- Structured markdown with consistent headings
- Machine-parseable sections (use `##` consistently)
- Short and factual (avoid prose, prefer tables/lists)

**Acceptance Criteria:**
- ContextBootstrap skill can extract deterministic context without scanning 59 projects
- Answers: "What services exist?", "How do I run X?", "Where is Y configured?"

### R3 – Platform Component READMEs
**Priority:** Medium
**Locations:**
- `backend/sources/Platform.Microservices/README.md`
- `backend/sources/Platform.Configuration/README.md`
- `backend/sources/Platform.Authorisation/README.md`
- `backend/sources/Platform.Monitoring/README.md`

**Purpose:** Document shared infrastructure patterns all services depend on

**Content (per component):**
- What this component provides
- How to use it (code examples)
- Configuration options
- Common patterns and anti-patterns
- References to example usage in existing services

**Acceptance Criteria:**
- A developer adding a new service knows which Platform.* components to reference
- Each README includes at least one working code example

### R4 – Core Business Service READMEs
**Priority:** Medium
**Locations (8 services):**
- `backend/sources/Order/README.md`
- `backend/sources/Store/README.md`
- `backend/sources/ShoppingCart/README.md`
- `backend/sources/Payment/README.md`
- `backend/sources/Customer/README.md`
- `backend/sources/Offer/README.md`
- `backend/sources/Security/README.md`
- `backend/sources/ApiGateway/README.md`

**Purpose:** Document complex business logic, service responsibilities, and integration points

**Content (per service):**
- Service responsibility (one sentence)
- Key endpoints / API surface
- Database entities and relationships
- Integration dependencies (which other services it calls)
- Configuration requirements
- Local testing approach

**Template Structure:**
```markdown
# {ServiceName}

## Responsibility
{One sentence: what this service does}

## Architecture
- Database: {entities/schema info}
- External dependencies: {list}
- Publishes events: {if applicable}
- Consumes events: {if applicable}

## API Surface
{Key endpoints or link to Swagger/OpenAPI}

## Configuration
{Required env vars or settings}

## Local Development
{How to run/test in isolation}

## Known Issues / TODOs
{Links to relevant issues or tech debt}
```

**Acceptance Criteria:**
- Each service README answers: "What does this do?", "How do I test it?", "What does it depend on?"

### R5 – Consolidated Catalog Documentation
**Priority:** Low
**Location:** `backend/sources/_CATALOGS.md` (at sources level)
**Purpose:** Explain catalog service patterns without duplicating 6+ similar READMEs

**Content:**
- What catalog services do (shared pattern)
- Naming convention: `*Catalog` = product search/browse, `*Proxy` = external integration
- Catalog services inventory:
  - ProductCatalog
  - TyreCatalog
  - RimCatalog
  - AccessoryProductCatalog
  - ServiceProductCatalog
  - WheelPackageCatalog
- Shared behaviors (caching, search, filtering)
- When to extend vs create new catalog

**Acceptance Criteria:**
- A developer understands the catalog pattern without reading all 6 service implementations

## Implementation Plan

### Phase 1: Root Documentation (High Impact, ~3 hours)
1. Create `/Users/dh/Documents/Dev/NCG/ncg-backend/README.md`
   - Extract and summarize content from `backend/sources/README.md`
   - Add quick start section with absolute minimal commands
   - Add repository structure map (ASCII tree or table)
   - Link to sources/README.md for detailed info
2. Create `/Users/dh/Documents/Dev/NCG/ncg-backend/AGENT.md`
   - Extract service list from sources/README.md (currently at line ~60-200 based on structure)
   - Build service responsibility matrix
   - Add common task recipes (from sources/README commands section)
   - Add "Where to find" routing table
3. Test: Run ContextBootstrap skill and verify it can extract deterministic context

### Phase 2: Platform Components (Medium Impact, ~4 hours)
1. Create template for Platform.* READMEs
2. For each Platform component:
   - Scan code to identify public APIs
   - Extract configuration patterns
   - Find 2-3 example usages in existing services
   - Write README from template
3. Review with actual service implementations to validate accuracy

### Phase 3: Core Services (Medium Impact, ~8 hours)
1. Create core service README template (see R4)
2. Prioritize by complexity/usage:
   - Order (highest priority - complex workflow)
   - Payment (integration risk)
   - Security (critical + IdentityServer config)
   - ApiGateway (routing + Ocelot config)
   - Store, ShoppingCart, Customer, Offer (business logic)
3. For each service:
   - Interview codebase (Controllers, Models, Infrastructure)
   - Extract configuration from appsettings/compose
   - Document database schema from EF migrations or Models
   - Write README

### Phase 4: Catalog Consolidation (Low Impact, ~1 hour)
1. Create `backend/sources/_CATALOGS.md`
2. Extract common patterns from existing catalog service code
3. Link from root README and AGENT.md

## Open Items

### [DECISION: README Template Standard]
Should all service READMEs follow a strict template or allow flexibility?
- **Option A:** Strict template (easier for agent parsing, consistent structure)
- **Option B:** Flexible with suggested sections (faster to write, adapts to service complexity)
- **Recommendation:** Option A for core services, Option B for smaller utilities/proxies

### [DECISION: AGENT.md vs ContextBootstrap Skill]
Should AGENT.md duplicate information from ContextBootstrap skill output, or should they reference each other?
- **Option A:** AGENT.md is static, ContextBootstrap augments it with dynamic discovery
- **Option B:** AGENT.md is comprehensive, ContextBootstrap only validates/refresh
- **Recommendation:** Option A (AGENT.md = baseline facts, skill adds runtime discovery)

### [MISSING: Service Responsibility Definitions]
Need to determine concise responsibility statements for all 59 services. Source options:
- Extract from existing sources/README.md service list
- Infer from controller endpoints and models
- Document in this plan iteration as discovered

### [DECISION: Documentation Maintenance Strategy]
Who keeps READMEs up to date?
- Add to PR checklist when service changes?
- Quarterly documentation review?
- Agent-assisted drift detection?
- **Recommendation:** Add "Update README if applicable" to PR template, quarterly agent audit

## Verification Test Cases

### Given: Fresh NCG repository clone
**When:** Developer runs `ContextBootstrap` skill at startup
**Then:** Agent extracts deterministic context including:
- Repository purpose
- 5+ runnable commands with sources
- Service inventory (at least 20 services with responsibilities)
- Links to Ops guides
- Confidence: Structure=high, Commands=high, Architecture=medium

### Given: Root README.md exists
**When:** New developer follows quick start guide
**Then:** Development stack runs successfully within 10 minutes

### Given: AGENT.md exists with service matrix
**When:** Agent is asked "What does the Order service do?"
**Then:** Agent answers from AGENT.md without scanning Order/ codebase

### Given: Platform.Microservices/README.md exists
**When:** Developer creates new service
**Then:** README provides working code example for base service setup

### Given: Order/README.md exists
**When:** Developer needs to debug order flow
**Then:** README identifies database entities, API endpoints, and dependent services

## Dependencies

- Access to NCG backend repository: `/Users/dh/Documents/Dev/NCG/ncg-backend`
- Existing comprehensive README at: `backend/sources/README.md`
- ContextBootstrap skill (recently updated)
- Documentation vault access: `/Users/dh/Documents/DanielsVault/ncg`

## Risk Assessment

**Low Risk:**
- Creating root README (additive, no breaking changes)
- AGENT.md creation (new file, no existing dependencies)

**Medium Risk:**
- Service README accuracy (might document outdated patterns if code is not reviewed)
- Maintenance burden (59 projects = potential documentation drift)

**Mitigation:**
- Start with root + AGENT.md only (Phase 1) to validate approach
- Use template-driven approach for consistency
- Mark sections with confidence levels (e.g., "Last verified: 2026-03-01")

## Success Metrics

- ContextBootstrap skill completes in <5 seconds with high-confidence output
- New developer onboarding time reduced from ~4 hours to <1 hour
- Agent sessions require 30% fewer codebase searches for routine questions
- Platform component adoption increases (measurable via NuGet package references)

---

## Iteration 2 (Refined) — Lean Context Files Strategy

### Why refinement was needed

Iteration 1 proposed many README files (platform + 8 core services + catalogs). In practice, this creates high maintenance overhead and drift risk in a fast-moving microservice repo.  
For agent effectiveness and developer onboarding, a **small set of high-signal context files** is more reliable than broad README coverage.

### Keep (high value, low drift risk)

1. **`/Users/dh/Documents/Dev/NCG/ncg-backend/README.md`** (new, concise entrypoint)
   - Purpose: orient from repo root; route quickly to `backend/sources/README.md`.
   - Must contain: quick start, repo map, branch strategy, links to canonical docs.

2. **`/Users/dh/Documents/Dev/NCG/ncg-backend/backend/sources/README.md`** (already exists, canonical detailed guide)
   - Keep as source-of-truth for commands, architecture, Docker/CI flows.
   - Enforce updates here first when workflows change.

3. **`/Users/dh/Documents/Dev/NCG/ncg-backend/backend/sources/AGENT.md`** (new, machine-oriented)
   - Purpose: deterministic agent bootstrap without broad filesystem scan.
   - Must contain only stable, parseable sections:
     - runnable command index
     - service/domain inventory (short responsibility matrix)
     - “where to find X” routing table
     - critical constraints (e.g., Ocelot merged file rule)

4. **`/Users/dh/Documents/Dev/NCG/ncg-backend/backend/sources/tests/README.md`** (new, focused on operational scripts)
   - Purpose: explain `check-build.sh`, `tests/lib/check-build/*`, and local watcher/analyze/pull/plan tools.
   - Must contain: script responsibilities, execution order, artifacts, failure semantics.

5. **`/Users/dh/Documents/Dev/NCG/ncg-backend/backend/sources/SERVICES_INVENTORY.md`** (new, compact index)
   - Purpose: quick lookup of services, db-context presence, migration path pattern, and key external dependencies.
   - Keep factual/tabular; avoid prose.

### Drop for now (nice-to-have)

- Per-component Platform READMEs (`Platform.*`) — helpful but redundant while `sources/README.md` and AGENT routing exist.
- 8 core business service READMEs — high effort/drift; better deferred until service ownership + maintenance rule is in place.
- `_CATALOGS.md` consolidated doc — low immediate impact compared to tests/CI/context bootstrap clarity.

### Updated implementation plan (minimal, execution-ready)

#### Phase A — Foundation Context (must-have)
1. Create root `README.md` (entrypoint + routing).
2. Create `backend/sources/AGENT.md` (strict machine-readable structure).
3. Create `backend/sources/tests/README.md` (check-build script architecture + watcher flow).
4. Create `SERVICES_INVENTORY.md` with compact tables.
5. Do **not** create `MIGRATION_STATUS.md`; migration reset to MariaDB 11.8.5 is completed and should remain documented in canonical docs/spec history only.

#### ContextBootstrap linkage strategy (resolved)
- Link ContextBootstrap to **specific high-signal files** in the docs repo, not broad folders:
  - `/Users/dh/Documents/DanielsVault/ncg/ncg-docs/docs/Ops/README.md`
  - `/Users/dh/Documents/DanielsVault/ncg/ncg-docs/docs/Ops/Environments/Development/Dev-Environment.md`
  - `/Users/dh/Documents/DanielsVault/ncg/ncg-docs/docs/Ops/Services/GitLab-CI-CD.md`
  - `/Users/dh/Documents/DanielsVault/ncg/ncg-docs/docs/Ops/Services/Service-Dependency-Graph.md`
  - `/Users/dh/Documents/DanielsVault/ncg/ncg-docs/docs/Ops/Security/Secrets-Management.md`
  - `/Users/dh/Documents/DanielsVault/ncg/ncg-docs/docs/Ops/Security/Certificates.md`
- Rationale: deterministic bootstrap, less noise, faster startup extraction, lower drift risk.

#### Phase B — Consistency & governance (must-have)
1. Remove/resolve stale references if files are missing (especially in `CLAUDE.md` or other guidance docs).
2. Add lightweight doc governance rule:
   - “Workflow or CI/script changes require updates to `sources/README.md` and `tests/README.md` if affected.”
3. Add “Last verified” stamp in AGENT + inventory files.

### Updated acceptance criteria

- Agent can answer with high confidence, without deep scan:
  - “How do I run/build/test?”
  - “How does check-build work?”
  - “Which services exist and where is dependency/security/pipeline documentation?”
- No duplicate conflicting command docs between root README and `sources/README.md`.
- Missing-file references are eliminated (especially `MIGRATION_STATUS.md` references if file is intentionally not used).
- Documentation update scope remains sustainable (<= 5 core context files in repo + targeted external doc anchors).

## History

| Date | Iteration | Author | Delta |
|---|---|---|---|
| 2026-03-01 | 1 | Copilot | Initial plan: defined requirements, phased implementation, identified 5 priority areas and 12 specific README locations |
| 2026-03-07 | 2 | Copilot | Refined to lean context strategy: kept only high-value files (root README, sources README, AGENT, tests README, SERVICES_INVENTORY, MIGRATION_STATUS), removed nice-to-have per-service/platform/cat docs for now |
| 2026-03-07 | 3 | Copilot | Refined after user update: removed MIGRATION_STATUS from must-have set, resolved ContextBootstrap linking to specific docs files in `ncg-docs`, tightened acceptance criteria to deterministic targeted anchors |

---

**SessionId:** Not yet assigned (will be added on next refinement)
