# Design

## Classification Decisions

| Source | Entity type | Reason |
|---|---|---|
| STS Onboarding parent | `type: spec` | Parent requirements/roadmap source for the STS rollout. |
| STS Secret Hygiene / Cert Lifecycle | `type: spec` | Active/root STS slice, explicit draft but operationally unblocked. |
| STS Distributed Rate Limit / Proxy Trust | `type: spec` | Optional post-go-live STS slice. |
| STS External Integration Network | `type: spec` | Optional post-gate STS slice. |
| STS Cross-Repo Check-Build | `type: spec` | Accepted support slice 04.1. |
| STS MariaDB Provider / DB Host Alignment | `type: spec` | Accepted support slice 04.2. |
| STS Deferred Topics TODO | `type: document` | Backlog/support artifact, not a current primary spec contract. |

## Metadata Quality

1. Accepted sources use `metadata_quality: explicit`.
2. Draft/optional sources keep their explicit status.
3. The parent onboarding source uses `metadata_quality: conflict` because the header is Draft while the roadmap records many gate-relevant completions.

## Runtime

No runtime validation is applicable for this metadata-only import.
