# Shared technical completion integration

The active shared entrypoints are `skills-repo/skills/implement`, `change-accepted` and `code-review`. Use these active paths or skill names, not preserved vendor entrypoints. The workflow requirements are maintained in the active OpenSpec change `add-sequential-ticket-orchestration-skill`, capability `technical-change-completion`; [ADR 0017](../adr/0017-three-sequential-refactoring-checks.md) records the accepted decision.

`code-review` owns review methodology and applicability. `change-accepted` owns the technical closeout transition. Repository AGENTS.md files and delivery/archive adapters reference them; repository-specific commands and standards stay local.

## Local ownership and vendor provenance

Daniel's requested central entrypoint retains the public name `code-review`. The active `code-review`, `implement` and `ask-matt` entries are now Daniel-owned directories, adopted from the preserved Matt Pocock snapshot. This keeps named callers stable while separating local policy from upstream updates. The snapshot and its lock remain unchanged. Vendor synchronization must continue to preserve owned directories, as required by the hybrid skill-sync contract; it must not replace them with vendor links.

| Active skill | Preserved source | Source SKILL.md SHA-256 at adoption |
| --- | --- | --- |
| code-review | `skills-repo/vendor/mattpocock/.agents/skills/code-review` | `47f4e52c21694def9c7c11cbfbf891ca35eac7a93e395797515be3c8a409ae50` |
| implement | `skills-repo/vendor/mattpocock/.agents/skills/implement` | `a83f5eeb80700628c6af781ba1d4ec6b220de2a4cb93d426929c180ae268a1d1` |
| ask-matt | `skills-repo/vendor/mattpocock/.agents/skills/ask-matt` | `b25d86fb36b1d294eeead5d7db529f86135f9671f2afcd607579a63bb2213769` |

Runtime links remain managed by `skills-repo/tools/sync-codex-skill-links.sh`. The ask-matt phase-boundary reference still uses the preserved snapshot. The local adaptation does not update any upstream repository, live batch ledger or automation.

## Migration scope

The shared repository, NCG backend's project and Git-root guidance, probare-crm, and ki-fuer-kmu use the shared completion entrypoints. The write-agents-md template emits references. ki-fuer-kmu retains local delivery mechanics in `change-accepted-closeout`; local OpenSpec archive entrypoints reuse completion evidence. Other application pilots keep their own lifecycle contracts.
