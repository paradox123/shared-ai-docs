# Unverbindliche Designreferenz: Backstage und React Flow

Der erste Prototyp zeigt mögliche Oberflächen und Interaktionen für den Operator Client. Er dient als visuelle Orientierung und Diskussionsgrundlage. Texte, Beispieldaten und simulierte Abläufe sind vorläufig und definieren keine zusätzlichen Anforderungen. Maßgeblich bleiben das jeweilige Ticket und die [zugehörige OpenSpec-Spezifikation](../../openspec/changes/add-agent-framework-operator-gui/specs/agent-framework-operator-gui/spec.md); weitere verbindliche Quellen stehen im [Spezifikationseinstieg](spec.md).

Abweichungen vom Prototyp sind zulässig. Erkennbare Anforderungslücken sind zu benennen, statt sie aus den Screens abzuleiten. Auch die im Prototyp verwendeten Bibliotheken und dessen Aufbau begründen für sich keine verbindliche Architekturentscheidung.

## Rückmeldung zum ersten Prototyp

Am 2026-09-14 hat der Nutzer die gestalterische Richtung des ersten Prototyps positiv bewertet. Die Texte bleiben überarbeitungsbedürftig. Daraus folgt weder die Auswahl einer bestimmten Variante noch eine fachliche Abnahme der gezeigten Funktionen.

## Code und lokale Vorschau

- Branch: `codex/prototype-backstage-react-flow`, ursprünglicher Prototyp-Commit `f804685`.
- Verzeichnis im Branch: `microsoft-agent-framework-work-package-pilot/operator-gui-prototype`.
- Einstieg: [Prototyp-README mit Start, Bedienwegen und Grenzen](../../../shared-ai-docs-backstage-prototype/microsoft-agent-framework-work-package-pilot/operator-gui-prototype/README.md). Dieser lokale Link setzt den vorhandenen benachbarten Worktree voraus; in einem anderen Checkout ist der Branch-/Verzeichnisverweis maßgeblich.
- Lokaler Worktree: `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs-backstage-prototype`.
- Start im Prototyp-Verzeichnis: einmal `npm ci`, anschließend `npm run prototype`.
- Vorschau: [A · Workflow-Werkbank](http://127.0.0.1:4317/prototype/agent-operations?variant=A), [B · Interventions-Inbox](http://127.0.0.1:4317/prototype/agent-operations?variant=B), [C · Repository und Mandat](http://127.0.0.1:4317/prototype/agent-operations?variant=C). Die Vorschau ist nur erreichbar, solange der lokale Server läuft.

Backstage und React Flow sind tatsächlich eingebunden. Backend-Funktionen, Daten, Berechtigungen, Agentenaktionen und Workstation-Verhalten sind simuliert; Demo-Zustände liegen im Arbeitsspeicher. Diese Simulation ersetzt keinen der in den Tickets geforderten realen Verhaltensnachweise. Der Prototyp liegt außerhalb von `main`.

## Einstieg für eine Implementierungs-Session

Den Ticketplatzhalter durch den konkreten Ticketpfad ersetzen:

> Implementiere Ticket `<Ticketpfad>` anhand der zugehörigen OpenSpec-Spezifikation und beachte seine Blocker. Berücksichtige den verlinkten Backstage-/React-Flow-Prototyp als unverbindliche Designreferenz. Texte, Screens und simulierte Abläufe definieren keine zusätzlichen Anforderungen. Benenne erkennbare Anforderungslücken, statt sie aus dem Prototyp abzuleiten. Lokal liegt der Prototyp unter `/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs-backstage-prototype/microsoft-agent-framework-work-package-pilot/operator-gui-prototype`; lies dort die `README.md`. Alternativ ist er im Branch `codex/prototype-backstage-react-flow` unter `microsoft-agent-framework-work-package-pilot/operator-gui-prototype` zu finden.
