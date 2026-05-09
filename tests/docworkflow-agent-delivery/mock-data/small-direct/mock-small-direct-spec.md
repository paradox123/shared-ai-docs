# Mock Small Direct Spec

## Goal

Exercise direct Agent Delivery for a tiny synthetic spec. This fixture must not create child-control artifacts.

## Requirement

Write one direct result file at `mock-target/output/small-direct-result.json` with:

```json
{
  "mode": "direct",
  "result": "ok",
  "source": "mock-small-direct"
}
```

## Boundaries

- No child index.
- No child specs.
- No child session handoffs.
- No real product repository or real product fixture input.

