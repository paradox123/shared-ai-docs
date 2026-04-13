# WatcherCommandMap

Canonical local commands:

- Arm next build:
  - `cd backend/sources && dotnet run tests/check-build.local.watch.cs -- --arm-next-build --project-id 4`
  - optional explicit branch: `... --branch <target-branch>`
- Start watcher:
  - `cd backend/sources && dotnet run tests/check-build.local.watch.cs -- --watch --project-id 4`
- Disarm:
  - `cd backend/sources && dotnet run tests/check-build.local.watch.cs -- --disarm`
- Show state:
  - `cd backend/sources && dotnet run tests/check-build.local.watch.cs -- --show-state`
