# Ignore deleted sessions in NCG wiki reviews

## Why

Daniel authorizes the NCG wiki automation to treat sessions that no longer exist as intentionally deleted and irrelevant. A missing rollout alone must not stop the review or require a new per-ID approval.

## What Changes

- Add an identity-bound `missing_session_policy: "ignore"` capture option, enabled for the NCG automation. Other callers retain the strict default and existing explicit carry allowlist.
- Admit only absent-storage rows with matching `missing_rollout` diagnostics; preserve raw resolver failures and report ignored IDs. Continue to reject unreadable, ambiguous, corrupt, incomplete or timed-out evidence.
- Remove ignored missing carry IDs only in successful atomic finalization, preserving every remaining carry object and order.
- Update the canonical workflow/schema documentation and the existing automation prompt without changing its schedule, target thread or source/delivery gates.

## Impact

The existing .NET file-based review/delivery helpers and their isolated public-CLI fixtures. No shared Python resolver-default change, NCG code/wiki edit, production action or premature live checkpoint advancement.
