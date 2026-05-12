---
name: agent-delivery-retro-review
description: Review Agent Delivery workflow quality after or during a change. Focus on active OpenSpec scope, skill bloat, cleanup safety, and validator coverage rather than launcher/controller/session evidence.
---

# agent-delivery-retro-review

Purpose: review whether Agent Delivery stayed focused.

Check:
- Was exactly one narrow OpenSpec change the active implementation context?
- Were parent/master specs reference-only?
- Did skills stay short and route to validators instead of carrying rule walls?
- Did cleanup classify delete/retain/archive-reference paths with reasons?
- Did validation prove deleted paths are not default workflow inputs?

Commands:

```sh
dotnet run skills-repo/tools/ValidateActiveOpenSpecScope.cs -- --change <change-name> [--parent <path>]
dotnet run skills-repo/tools/ValidateAgentDeliveryCleanup.cs -- --manifest openspec/changes/<change-name>/cleanup-manifest.json --root <repo-root>
dotnet run skills-repo/tools/ValidateSkillProseBudget.cs -- --root <repo-root>
```

Output findings first, ordered by severity, with concrete file references.
