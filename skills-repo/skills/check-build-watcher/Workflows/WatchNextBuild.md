# WatchNextBuild

## Goal
Translate watcher intents into deterministic local commands for NCG check-build automation.

## Preconditions
- Repository root is `/Users/dh/Documents/Dev/NCG/ncg-backend`.
- `backend/sources/tests/check-build.local.watch.cs` exists.
- `GITLAB_PAT` is set (or explicit `--token` provided).

## Command Mapping
1. **Arm next build**
   - Trigger: `watch my next build`, `watch next build`, `beobachte meinen nächsten build`
   - Command:
     - `cd backend/sources && dotnet run tests/check-build.local.watch.cs -- --arm-next-build --project-id <project-id>`
     - optional explicit branch override: `... --branch <branch>`
2. **Start watch loop**
   - Trigger: `start watcher`, `watch now`, `run watcher`
   - Command:
     - `cd backend/sources && dotnet run tests/check-build.local.watch.cs -- --watch --project-id <project-id>`
3. **One-shot poll**
   - Trigger: `watch once`, `check once`
   - Command:
     - `cd backend/sources && dotnet run tests/check-build.local.watch.cs -- --once --project-id <project-id>`
4. **Disarm**
   - Trigger: `disarm watcher`, `stop watching next build`
   - Command:
     - `cd backend/sources && dotnet run tests/check-build.local.watch.cs -- --disarm`
5. **Show state**
   - Trigger: `show watcher state`, `watch status`
   - Command:
     - `cd backend/sources && dotnet run tests/check-build.local.watch.cs -- --show-state`

## Defaults
- `project-id`: `4` when user does not specify.
- `branch`: auto-detect current git branch when user does not specify (fallback: last stored watcher branch; otherwise require explicit `--branch`).
- trigger mode: `failed-or-incident-marker`.
- arm mode: keep armed until success (unless one-shot explicitly requested).

## Guardrails
- Do not ask for GitLab pipeline URL for generic watcher intents.
- Use local watcher flow first; only inspect specific pipeline URLs when user explicitly requests manual inspection.
- Keep code-fix/commit/push manual.
- When automation reports incidents, explicitly point to generated diagnosis artifacts (`analysis/diagnosis.json` and `diagnosis/warmup-summary.json`) so warmup/healthcheck failures are visible without extra digging.
