---
name: check-build-watcher
description: Developer-armed watcher flow for NCG check-build automation. USE WHEN user says "watch my next build", "watch next build", or asks to arm/disarm/show local check-build watcher state.
---

# CheckBuildWatcher

Maps natural-language watch prompts to the local `check-build.local.watch.cs` workflow in `backend/sources`.

## Workflow Routing

| Workflow | Trigger | File |
|----------|---------|------|
| **WatchNextBuild** | "watch my next build" OR "watch next build" OR "beobachte meinen nächsten build" OR "arm watcher" OR "disarm watcher" | `Workflows/WatchNextBuild.md` |

## Examples

**Example 1: Arm watcher from prompt**
```
User: "watch my next build"
→ Invokes WatchNextBuild workflow
→ Arms local watcher intent for next relevant pipeline
```

**Example 2: Start watcher loop**
```
User: "start watching now"
→ Invokes WatchNextBuild workflow
→ Starts --watch polling mode using local state + GITLAB_PAT
```

**Example 3: Check current watcher state**
```
User: "show watcher state"
→ Invokes WatchNextBuild workflow
→ Runs --show-state and returns current arm/processed status
```
