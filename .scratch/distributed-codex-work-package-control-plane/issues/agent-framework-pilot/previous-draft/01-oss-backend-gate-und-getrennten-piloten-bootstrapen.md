# 01: OSS-Backend-Gate beweisen und getrennten Piloten bootstrapen

> Wiederhergestellter Vorentwurf; durch den freigegebenen 14-Ticket-Backlog ersetzt.

**What to build:** Vor dem fachlichen Agent-Framework-Spike wird nachgewiesen, dass der genaue MAF-/Durable-Stack einen produktionsfähigen, selbst hostbaren Open-Source-Backendpfad ohne verpflichtende zusätzliche Framework- oder Managed-Workflow-Service-Lizenzkosten besitzt. Erst danach entsteht der neue Top-Level-Ordner `microsoft-agent-framework-work-package-pilot/`.

**Blocked by:** None

**Covers:** US 129-132; OpenSpec-Anforderung „Workflow infrastructure has a licence-cost-free open-source path“

**LangGraph baseline:** Der bestehende `langgraph-github-issue-pilot/`, seine Cloudflare-/macOS-Anbindung, Runtime-Daten und Worktrees bleiben unverändert.

**Status:** needs-triage

- [ ] Ein kleiner aktiver OpenSpec-Change beschreibt Scope, Write-Set, Lizenzprüfung, direkte Verifikation und Abbruchgrenze.
- [ ] Die Lizenzen aller direkten und transitiven Workflow-/Backendkomponenten sowie unvermeidbare Servicekosten sind versioniert inventarisiert.
- [ ] Ein produktionsfähiger selbst verwalteter Backendkandidat wird mit dem exakt gepinnten Durable-Extension-Tuple kompiliert und ausgeführt; der In-Memory-Emulator allein genügt nicht.
- [ ] Zwei getrennte Worker-Prozesse beweisen Recovery desselben Testlaufs über den Backendkandidaten.
- [ ] Bei fehlender Kompatibilität oder verpflichtendem Paid Service endet das Ticket mit einem dokumentierten No-Go; keine weiteren MAF-Slices werden implementiert.
- [ ] Nach bestandenem Gate entsteht ausschließlich `microsoft-agent-framework-work-package-pilot/` mit eigenen Paket-, Config-, Daten-, Prozess- und Cleanup-Grenzen.
- [ ] Ein Nichtbeeinflussungsnachweis zeigt vor und nach dem Bootstrap identische LangGraph-, Cloudflare-, macOS- und ProBara-CRM-Zustände.

## Session lesson

Der installierte LangGraph-Pilot wich zeitweise vom getesteten Source-/Contract-Stand ab. Deshalb zeichnet der Bootstrap Source-Commit, Package-Lock, Runtime, Config-Digest und Contract-Version auf und lehnt inkompatible Kombinationen vor einem Issue-Start ab.
