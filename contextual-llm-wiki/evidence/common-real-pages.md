<!-- concepts/liquiditätsreserve -->
---
title: Liquiditätsreserve
summary: Die Liquiditätsreserve ist der heute frei verfügbare Geldbetrag zur Deckung laufender Ausgaben; im beschriebenen Portfolio beträgt sie 2000 Euro.
sources:
  - private/README.md
  - probare-crm/README.md
kind: concept
createdAt: "2026-09-13T09:05:54.698Z"
updatedAt: "2026-09-13T09:05:54.698Z"
tags:
  - Liquidität
  - Private Finanzen
aliases:
  - liquiditätsreserve
confidence: 1
provenanceState: merged
modelId: codex-cli-default
promptVersion: v3
promptModifiers:
  - lang=de
---

# Liquiditätsreserve

Die Liquiditätsreserve ist der heute frei verfügbare Geldbetrag zur Deckung laufender Ausgaben. Erwartete, noch nicht eingegangene Zahlungen zählen nicht zur heutigen Liquidität. ([private/README.md Zeilen 3–5](obsidian://open?path=%2Fprivate%2Fvar%2Ffolders%2Fwb%2Frpvbdznn4g3f4s2k4nwbn24c0000gn%2FT%2Fwiki-behavior-dP4CPl%2Falpha%2FREADME.md))

## Aktueller Bestand und Zeitraum

Das persönliche Portfolio verfügt aktuell über eine frei verfügbare Reserve von 2.000 Euro. Diese soll die laufenden Ausgaben bis Oktober decken. ([private/README.md Zeilen 5–5](obsidian://open?path=%2Fprivate%2Fvar%2Ffolders%2Fwb%2Frpvbdznn4g3f4s2k4nwbn24c0000gn%2FT%2Fwiki-behavior-dP4CPl%2Falpha%2FREADME.md))

## [Erwarteter Zahlungseingang](erwarteter-zahlungseingang.md)

Ein laufender Projektvertrag sieht einen Zahlungseingang von 5.000 Euro im Oktober vor. Der Betrag steht erst nach seinem Eingang zur Verfügung und darf vorher nicht als verfügbare Reserve gerechnet werden. Für die Liquiditätsplanung ist deshalb die zeitliche Trennung zwischen heute verfügbaren Mitteln und erwarteten Zahlungen relevant. ([probare-crm/README.md Zeilen 5–5](obsidian://open?path=%2Fprivate%2Fvar%2Ffolders%2Fwb%2Frpvbdznn4g3f4s2k4nwbn24c0000gn%2FT%2Fwiki-behavior-dP4CPl%2Fbeta%2FREADME.md))

## Sources

- [private/README.md](obsidian://open?path=%2Fprivate%2Fvar%2Ffolders%2Fwb%2Frpvbdznn4g3f4s2k4nwbn24c0000gn%2FT%2Fwiki-behavior-dP4CPl%2Falpha%2FREADME.md)
- [probare-crm/README.md](obsidian://open?path=%2Fprivate%2Fvar%2Ffolders%2Fwb%2Frpvbdznn4g3f4s2k4nwbn24c0000gn%2FT%2Fwiki-behavior-dP4CPl%2Fbeta%2FREADME.md)


## Originalquellen

- [private/README.md](obsidian://open?path=%2Fprivate%2Fvar%2Ffolders%2Fwb%2Frpvbdznn4g3f4s2k4nwbn24c0000gn%2FT%2Fwiki-behavior-dP4CPl%2Falpha%2FREADME.md) — SHA-256 43052006006b4b7dcf5b6f9f44b03a3d4675f845815c38f76e65d1e181fe5692
- [probare-crm/README.md](obsidian://open?path=%2Fprivate%2Fvar%2Ffolders%2Fwb%2Frpvbdznn4g3f4s2k4nwbn24c0000gn%2FT%2Fwiki-behavior-dP4CPl%2Fbeta%2FREADME.md) — SHA-256 7b3cdf1d6463228b11c4bd0e94b1f7852a3ae53eb109a57b27c825f137d2da9a


---

<!-- concepts/zeitliche-ausgabendeckung-durch-reserven -->
---
title: Zeitliche Ausgabendeckung durch Reserven
summary: Die verfügbare Reserve soll laufende Ausgaben über einen festgelegten Zeitraum decken, im beschriebenen Fall bis Oktober.
sources:
  - private/README.md
kind: concept
createdAt: "2026-09-13T09:05:55.647Z"
updatedAt: "2026-09-13T09:05:55.647Z"
tags:
  - Liquiditätsplanung
  - Ausgabendeckung
aliases:
  - zeitliche-ausgabendeckung-durch-reserven
  - ZADR
confidence: 1
provenanceState: extracted
modelId: codex-cli-default
promptVersion: v3
promptModifiers:
  - lang=de
---

# Zeitliche Ausgabendeckung durch Reserven

Die zeitliche Ausgabendeckung durch Reserven beschreibt, für welchen Zeitraum heute frei verfügbares Geld laufende Ausgaben decken soll. Grundlage ist die [Liquiditätsreserve](liquidit%C3%A4tsreserve.md), also der aktuell frei verfügbare Geldbetrag. ([private/README.md Zeilen 3–5](obsidian://open?path=%2Fprivate%2Fvar%2Ffolders%2Fwb%2Frpvbdznn4g3f4s2k4nwbn24c0000gn%2FT%2Fwiki-behavior-dP4CPl%2Falpha%2FREADME.md))

## Verfügbarer Betrag und Zielzeitraum

Im beschriebenen persönlichen Portfolio stehen heute **2.000 Euro** als frei verfügbare Reserve bereit. Diese Reserve soll die laufenden Ausgaben **bis Oktober** decken. Der genannte Zeitraum ist damit ein Deckungsziel. ([private/README.md Zeilen 5–5](obsidian://open?path=%2Fprivate%2Fvar%2Ffolders%2Fwb%2Frpvbdznn4g3f4s2k4nwbn24c0000gn%2FT%2Fwiki-behavior-dP4CPl%2Falpha%2FREADME.md))

Ob die Reserve tatsächlich bis Oktober reicht, lässt sich aus dem Betrag allein nicht bestimmen. Dafür müssten auch die Höhe und die zeitliche Verteilung der laufenden Ausgaben bekannt sein.

## Abgrenzung zu erwarteten Zahlungen

Erwartete, aber noch nicht eingegangene Zahlungen zählen nicht zur heutigen Liquidität. Für die Deckung durch die aktuell verfügbare Reserve ist daher zwischen vorhandenem Geld und erwarteten Zahlungseingängen zu unterscheiden. ([private/README.md Zeilen 3–5](obsidian://open?path=%2Fprivate%2Fvar%2Ffolders%2Fwb%2Frpvbdznn4g3f4s2k4nwbn24c0000gn%2FT%2Fwiki-behavior-dP4CPl%2Falpha%2FREADME.md))

## Sources

- Liquiditätsreserve](private/README.md)


## Originalquellen

- [private/README.md](obsidian://open?path=%2Fprivate%2Fvar%2Ffolders%2Fwb%2Frpvbdznn4g3f4s2k4nwbn24c0000gn%2FT%2Fwiki-behavior-dP4CPl%2Falpha%2FREADME.md) — SHA-256 43052006006b4b7dcf5b6f9f44b03a3d4675f845815c38f76e65d1e181fe5692


---

<!-- concepts/abgrenzung-erwarteter-zahlungen-von-heutiger-liquidität -->
---
title: Abgrenzung erwarteter Zahlungen von heutiger Liquidität
summary: Erwartete Zahlungen zählen erst nach ihrem Eingang zur heutigen Liquidität und sind zuvor kein Bestandteil der frei verfügbaren Reserve.
sources:
  - private/README.md
kind: concept
createdAt: "2026-09-13T09:06:06.003Z"
updatedAt: "2026-09-13T09:06:06.003Z"
tags:
  - Liquidität
  - Zahlungseingänge
aliases:
  - abgrenzung-erwarteter-zahlungen-von-heutiger-liquidität
  - AEZVHL
confidence: 1
provenanceState: extracted
modelId: codex-cli-default
promptVersion: v3
promptModifiers:
  - lang=de
---

# Abgrenzung erwarteter Zahlungen von heutiger Liquidität

## Grundprinzip

Die [Liquiditätsreserve](liquidit%C3%A4tsreserve.md) umfasst den heute frei verfügbaren Geldbetrag zur Deckung laufender Ausgaben. Erwartete Zahlungen, die noch nicht eingegangen sind, zählen nicht zur heutigen Liquidität. Entscheidend ist damit die aktuelle Verfügbarkeit des Geldes. ([private/README.md Zeilen 3–5](obsidian://open?path=%2Fprivate%2Fvar%2Ffolders%2Fwb%2Frpvbdznn4g3f4s2k4nwbn24c0000gn%2FT%2Fwiki-behavior-dP4CPl%2Falpha%2FREADME.md))

## Anwendung auf das persönliche Portfolio

Das persönliche Portfolio verfügt heute über eine frei verfügbare Reserve von **2.000 Euro**. Diese soll die laufenden Ausgaben bis Oktober decken. Noch ausstehende, erwartete Zahlungen werden dieser heutigen Reserve nicht zugerechnet. ([private/README.md Zeilen 5–5](obsidian://open?path=%2Fprivate%2Fvar%2Ffolders%2Fwb%2Frpvbdznn4g3f4s2k4nwbn24c0000gn%2FT%2Fwiki-behavior-dP4CPl%2Falpha%2FREADME.md))

## Sources

- Liquiditätsreserve](private/README.md)


## Originalquellen

- [private/README.md](obsidian://open?path=%2Fprivate%2Fvar%2Ffolders%2Fwb%2Frpvbdznn4g3f4s2k4nwbn24c0000gn%2FT%2Fwiki-behavior-dP4CPl%2Falpha%2FREADME.md) — SHA-256 43052006006b4b7dcf5b6f9f44b03a3d4675f845815c38f76e65d1e181fe5692


---

<!-- concepts/designportfolio -->
---
title: Designportfolio
summary: Eine Sammlung von Gestaltungsarbeiten, die im Dokument als Designkatalog präsentiert wird.
sources:
  - private/control.md
kind: concept
createdAt: "2026-09-13T09:06:04.219Z"
updatedAt: "2026-09-13T09:06:04.219Z"
tags:
  - Design
  - Portfolio
aliases:
  - designportfolio
confidence: 1
provenanceState: extracted
modelId: codex-cli-default
promptVersion: v3
promptModifiers:
  - lang=de
---

# Designportfolio

Ein **Designportfolio** ist eine Sammlung von Gestaltungsarbeiten. Im vorliegenden Dokument wird es als Designkatalog beschrieben, der blaue Umschläge und [Typografische Entwürfe](typografische-entw%C3%BCrfe.md) zeigt. Passende verwandte Konzepte sind [Umschlaggestaltung](umschlaggestaltung.md) und Typografie. ([private/control.md Zeilen 1–3](obsidian://open?path=%2Fprivate%2Fvar%2Ffolders%2Fwb%2Frpvbdznn4g3f4s2k4nwbn24c0000gn%2FT%2Fwiki-behavior-dP4CPl%2Falpha%2Fcontrol.md))

## Abgrenzung

Der Begriff „Portfolio“ bezeichnet hier gestalterische Arbeiten. Das beschriebene Portfolio enthält keine Angaben zu Geldreserven, Einnahmen oder Zahlungszeitpunkten. ([private/control.md Zeilen 3–3](obsidian://open?path=%2Fprivate%2Fvar%2Ffolders%2Fwb%2Frpvbdznn4g3f4s2k4nwbn24c0000gn%2FT%2Fwiki-behavior-dP4CPl%2Falpha%2Fcontrol.md))

## Sources

- [private/control.md](obsidian://open?path=%2Fprivate%2Fvar%2Ffolders%2Fwb%2Frpvbdznn4g3f4s2k4nwbn24c0000gn%2FT%2Fwiki-behavior-dP4CPl%2Falpha%2Fcontrol.md) — „Portfolio als Designkatalog“


## Originalquellen

- [private/control.md](obsidian://open?path=%2Fprivate%2Fvar%2Ffolders%2Fwb%2Frpvbdznn4g3f4s2k4nwbn24c0000gn%2FT%2Fwiki-behavior-dP4CPl%2Falpha%2Fcontrol.md) — SHA-256 2838e87f27e9778666944f392c32cf722bd98c69c6b311b931fdeb7ae3c488a3


---

<!-- concepts/umschlaggestaltung -->
---
title: Umschlaggestaltung
summary: Blaue Umschläge werden im Designportfolio als Gestaltungsarbeiten gezeigt.
sources:
  - private/control.md
kind: concept
createdAt: "2026-09-13T09:06:11.845Z"
updatedAt: "2026-09-13T09:06:11.845Z"
tags:
  - Design
  - Umschlaggestaltung
aliases:
  - umschlaggestaltung
confidence: 1
provenanceState: extracted
modelId: codex-cli-default
promptVersion: v3
promptModifiers:
  - lang=de
---

# Umschlaggestaltung

Die Umschlaggestaltung ist im beschriebenen [Designportfolio](designportfolio.md) durch blaue Umschläge vertreten. Daneben zeigt das Portfolio [Typografische Entwürfe](typografische-entw%C3%BCrfe.md) und stellt damit auch einen Bezug zur Typografie her. ([private/control.md Zeilen 3–3](obsidian://open?path=%2Fprivate%2Fvar%2Ffolders%2Fwb%2Frpvbdznn4g3f4s2k4nwbn24c0000gn%2FT%2Fwiki-behavior-dP4CPl%2Falpha%2Fcontrol.md))

## Kontext im Portfolio

Portfolio bezeichnet hier eine Sammlung von Gestaltungsarbeiten. Das Dokument enthält keine Angaben zu Geldreserven, Einnahmen oder Zahlungszeitpunkten. ([private/control.md Zeilen 3–3](obsidian://open?path=%2Fprivate%2Fvar%2Ffolders%2Fwb%2Frpvbdznn4g3f4s2k4nwbn24c0000gn%2FT%2Fwiki-behavior-dP4CPl%2Falpha%2Fcontrol.md))

## Sources

- [Portfolio als Designkatalog](obsidian://open?path=%2Fprivate%2Fvar%2Ffolders%2Fwb%2Frpvbdznn4g3f4s2k4nwbn24c0000gn%2FT%2Fwiki-behavior-dP4CPl%2Falpha%2Fcontrol.md)


## Originalquellen

- [private/control.md](obsidian://open?path=%2Fprivate%2Fvar%2Ffolders%2Fwb%2Frpvbdznn4g3f4s2k4nwbn24c0000gn%2FT%2Fwiki-behavior-dP4CPl%2Falpha%2Fcontrol.md) — SHA-256 2838e87f27e9778666944f392c32cf722bd98c69c6b311b931fdeb7ae3c488a3


---

<!-- concepts/typografische-entwürfe -->
---
title: Typografische Entwürfe
summary: Das Designportfolio enthält Entwürfe zur typografischen Gestaltung.
sources:
  - private/control.md
kind: concept
createdAt: "2026-09-13T09:06:16.040Z"
updatedAt: "2026-09-13T09:06:16.040Z"
tags:
  - Design
  - Typografie
aliases:
  - typografische-entwürfe
confidence: 1
provenanceState: extracted
modelId: codex-cli-default
promptVersion: v3
promptModifiers:
  - lang=de
---

# Typografische Entwürfe

Typografische Entwürfe sind Teil des beschriebenen [Designportfolios](designportfolio.md), das auch blaue Umschläge zeigt. Das Portfolio bezeichnet hier eine Sammlung von Gestaltungsarbeiten. ([private/control.md Zeilen 3–3](obsidian://open?path=%2Fprivate%2Fvar%2Ffolders%2Fwb%2Frpvbdznn4g3f4s2k4nwbn24c0000gn%2FT%2Fwiki-behavior-dP4CPl%2Falpha%2Fcontrol.md))

## Kontext

Die Entwürfe werden im Zusammenhang mit einem Portfolio als Designkatalog genannt. Nähere Angaben zu ihrer Gestaltung enthält die Quelle nicht. Das Dokument macht außerdem keine Angaben zu Geldreserven, Einnahmen oder Zahlungszeitpunkten. ([private/control.md Zeilen 1–3](obsidian://open?path=%2Fprivate%2Fvar%2Ffolders%2Fwb%2Frpvbdznn4g3f4s2k4nwbn24c0000gn%2FT%2Fwiki-behavior-dP4CPl%2Falpha%2Fcontrol.md))

## Sources

- [Portfolio als Designkatalog](obsidian://open?path=%2Fprivate%2Fvar%2Ffolders%2Fwb%2Frpvbdznn4g3f4s2k4nwbn24c0000gn%2FT%2Fwiki-behavior-dP4CPl%2Falpha%2Fcontrol.md)


## Originalquellen

- [private/control.md](obsidian://open?path=%2Fprivate%2Fvar%2Ffolders%2Fwb%2Frpvbdznn4g3f4s2k4nwbn24c0000gn%2FT%2Fwiki-behavior-dP4CPl%2Falpha%2Fcontrol.md) — SHA-256 2838e87f27e9778666944f392c32cf722bd98c69c6b311b931fdeb7ae3c488a3


---

<!-- concepts/erwarteter-zahlungseingang -->
---
title: Erwarteter Zahlungseingang
summary: Der Projektvertrag sieht einen Zahlungseingang von 5000 Euro im Oktober vor, der erst nach Eingang als verfügbare Reserve zählt.
sources:
  - probare-crm/README.md
kind: concept
createdAt: "2026-09-13T09:06:23.663Z"
updatedAt: "2026-09-13T09:06:23.663Z"
tags:
  - zahlungseingang
  - projektvertrag
aliases:
  - erwarteter-zahlungseingang
confidence: 1
provenanceState: extracted
modelId: codex-cli-default
promptVersion: v3
promptModifiers:
  - lang=de
---

# Erwarteter Zahlungseingang

Ein erwarteter Zahlungseingang ist ein Betrag, dessen Eingang vorgesehen ist, der aber erst nach tatsächlichem Zahlungseingang zur Verfügung steht. Im beschriebenen Fall sieht ein laufender Projektvertrag einen Zahlungseingang von 5.000 Euro im Oktober vor. ([probare-crm/README.md Zeilen 5–5](obsidian://open?path=%2Fprivate%2Fvar%2Ffolders%2Fwb%2Frpvbdznn4g3f4s2k4nwbn24c0000gn%2FT%2Fwiki-behavior-dP4CPl%2Fbeta%2FREADME.md))

## Abgrenzung zur [Liquiditätsreserve](liquidit%C3%A4tsreserve.md)

Die [Liquiditätsreserve](liquidit%C3%A4tsreserve.md) umfasst den heute frei verfügbaren Geldbetrag zur Deckung laufender Ausgaben. Ein erwarteter Zahlungseingang darf vor seinem Eingang nicht als verfügbare Reserve gerechnet werden. ([probare-crm/README.md Zeilen 3–5](obsidian://open?path=%2Fprivate%2Fvar%2Ffolders%2Fwb%2Frpvbdznn4g3f4s2k4nwbn24c0000gn%2FT%2Fwiki-behavior-dP4CPl%2Fbeta%2FREADME.md))

## Bedeutung für die Ausgabenplanung

Für die Planung laufender Ausgaben ist die zeitliche Trennung zwischen erwartetem Zahlungseingang und bereits verfügbarem Geld relevant. Die im Oktober vorgesehenen 5.000 Euro stehen erst nach Zahlungseingang zur Verfügung. ([probare-crm/README.md Zeilen 5–5](obsidian://open?path=%2Fprivate%2Fvar%2Ffolders%2Fwb%2Frpvbdznn4g3f4s2k4nwbn24c0000gn%2FT%2Fwiki-behavior-dP4CPl%2Fbeta%2FREADME.md))

## Sources

- Liquiditätsreserve](probare-crm/README.md)


## Originalquellen

- [probare-crm/README.md](obsidian://open?path=%2Fprivate%2Fvar%2Ffolders%2Fwb%2Frpvbdznn4g3f4s2k4nwbn24c0000gn%2FT%2Fwiki-behavior-dP4CPl%2Fbeta%2FREADME.md) — SHA-256 7b3cdf1d6463228b11c4bd0e94b1f7852a3ae53eb109a57b27c825f137d2da9a


---

<!-- concepts/zeitliche-abgrenzung-verfügbarer-liquidität -->
---
title: Zeitliche Abgrenzung verfügbarer Liquidität
summary: Für die Planung laufender Ausgaben müssen heute verfügbare Mittel von zukünftigen Zahlungseingängen getrennt werden.
sources:
  - probare-crm/README.md
kind: concept
createdAt: "2026-09-13T09:06:27.663Z"
updatedAt: "2026-09-13T09:06:27.663Z"
tags:
  - liquidität
  - ausgabenplanung
aliases:
  - zeitliche-abgrenzung-verfügbarer-liquidität
  - ZAVL
confidence: 1
provenanceState: extracted
modelId: codex-cli-default
promptVersion: v3
promptModifiers:
  - lang=de
---

# Zeitliche Abgrenzung verfügbarer Liquidität

Die zeitliche Abgrenzung verfügbarer Liquidität unterscheidet zwischen heute frei verfügbarem Geld und künftig erwarteten Zahlungseingängen. Zur [Liquiditätsreserve](liquidit%C3%A4tsreserve.md) gehört nur der heute frei verfügbare Geldbetrag zur Deckung laufender Ausgaben. Erwartete Zahlungen dürfen vor ihrem Eingang nicht als verfügbare Reserve gerechnet werden. ([probare-crm/README.md Zeilen 3–5](obsidian://open?path=%2Fprivate%2Fvar%2Ffolders%2Fwb%2Frpvbdznn4g3f4s2k4nwbn24c0000gn%2FT%2Fwiki-behavior-dP4CPl%2Fbeta%2FREADME.md))

## Beispiel: Zahlung aus einem Projektvertrag

Ein laufender Projektvertrag sieht einen Zahlungseingang von 5.000 Euro im Oktober vor. Dieser Betrag steht erst nach dem tatsächlichen Zahlungseingang zur Verfügung und zählt vorher nicht zur verfügbaren [Liquiditätsreserve](liquidit%C3%A4tsreserve.md). ([probare-crm/README.md Zeilen 5–5](obsidian://open?path=%2Fprivate%2Fvar%2Ffolders%2Fwb%2Frpvbdznn4g3f4s2k4nwbn24c0000gn%2FT%2Fwiki-behavior-dP4CPl%2Fbeta%2FREADME.md))

## Bedeutung für die Ausgabenplanung

Für die Liquiditätsplanung laufender Ausgaben ist diese zeitliche Trennung relevant: Ein vereinbarter künftiger Zahlungseingang ist noch kein heute verfügbarer Geldbetrag zur Deckung dieser Ausgaben. ([probare-crm/README.md Zeilen 3–5](obsidian://open?path=%2Fprivate%2Fvar%2Ffolders%2Fwb%2Frpvbdznn4g3f4s2k4nwbn24c0000gn%2FT%2Fwiki-behavior-dP4CPl%2Fbeta%2FREADME.md))

## Sources

- Liquiditätsreserve](probare-crm/README.md)


## Originalquellen

- [probare-crm/README.md](obsidian://open?path=%2Fprivate%2Fvar%2Ffolders%2Fwb%2Frpvbdznn4g3f4s2k4nwbn24c0000gn%2FT%2Fwiki-behavior-dP4CPl%2Fbeta%2FREADME.md) — SHA-256 7b3cdf1d6463228b11c4bd0e94b1f7852a3ae53eb109a57b27c825f137d2da9a
