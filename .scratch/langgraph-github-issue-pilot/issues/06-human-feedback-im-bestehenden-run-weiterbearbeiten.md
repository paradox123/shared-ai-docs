# 06: Human-Feedback im bestehenden Run weiterbearbeiten

**What to build:** Daniels Aenderungswuensche an einem Pull Request setzen denselben persistenten Lauf fort, invalidieren veraltete Freigaben und fuehren zu einer neuen commit-genauen Implementierungs-, Evidence- und Review-Runde.

**Blocked by:** 05: Review-Fehler automatisch beheben und begrenzen

**Covers:** US 46, 61-67

**Status:** ready-for-agent

- [ ] Vor der Implementierung beschreibt ein kleiner aktiver OpenSpec-Change Ziel, Scope, Write-Set und direkte Verifikation dieses Slices und besteht die strikte Validierung.
- [ ] Ein menschlicher Change Request am zugehoerigen PR wird demselben LangGraph-Lauf und Worktree zugeordnet, statt einen neuen Implementierungsauftrag zu erzeugen.
- [ ] Jeder neue menschliche Feedback-Batch startet mit einem eigenen Drei-Runden-Zaehler und uebergibt nur das neue Feedback sowie den weiterhin gueltigen Issue- und Requirements-Kontext.
- [ ] Ein neuer PR-Commit entfernt `verified` und `awaiting-review`, setzt `agent-running` und invalidiert alle Evidence- und Review-Verdicts des vorherigen Heads.
- [ ] Nach der Aenderung werden Evidence fuer den neuen Head sowie alle drei Reviews vollstaendig neu erzeugt; eine vorherige Freigabe kann nicht wiederverwendet werden.
- [ ] Ein menschlich gemergter Pull Request schliesst das Issue, beendet den Lauf und hinterlaesst GitHub und LangGraph in demselben Abschlusszustand.
- [ ] Der Workflow merged, deployt oder released unter keinen Umstaenden selbst und interpretiert eine blosse PR-Aktivitaet nicht als menschliche Freigabe.
- [ ] Systemtests beweisen Feedback-Fortsetzung, getrennte Batch-Zaehler, Head-Invalidierung und menschlichen Merge-Abschluss ueber das produktive Interface.
