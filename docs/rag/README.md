# DanielsVault Local RAG

Dies ist der Einstiegspunkt fuer die RAG-Dokumentation in diesem Ordner.

## Start Here

- [DanielsVault Local RAG](/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/docs/rag/danielsvault-local-rag.md)
  Zielbild, Scope, Domain-Grenzen und empfohlener technischer Zuschnitt.
- [Evaluation Set v0](/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/docs/rag/evaluation-set.md)
  Eval-Set mit echten historischen Nutzerfragen, beobachteten Agent-Lookups, hilfreichen Gegenfragen und zukunftsorientierten Folgefragen.
- [Runtime Closeout 2026-04-23](/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/docs/rag/2026-04-23-rag-runtime-closeout.md)
  Abschlussbericht mit voller Verifikations-Checklist, Runtime-Validierung und OpenSpec-Archivpfaden.
- [Parent Spec](/Users/dh/Documents/DanielsVault/_shared/shared-ai-docs/_specs/2026-04-13%20DanielsVault%20Local%20RAG%20Wissensplattform.md)
  Uebergeordnete Anforderungen, Scope-Grenzen und offene Entscheidungen fuer das Projekt.

## Warum das Eval-Set hier zentral ist

Das Eval-Set ist nicht nur ein spaeterer Testanhang, sondern die Referenz dafuer, ob das RAG im Alltag wirklich nuetzlich ist.

Es deckt vier Fragetypen ab:

1. `historical-user`
2. `historical-agent`
3. `counterfactual-helpful`
4. `future`

Damit laesst sich messen, ob das RAG:

- die richtige Domain zuerst trifft
- die richtige Datei priorisiert
- Agenten beim Kontextaufbau hilft
- unnoetige Cross-Domain-Suche reduziert

## Empfohlene Lesereihenfolge

1. Zielbild lesen
2. Parent-Spec lesen
3. Evaluation Set lesen
4. Runtime-Closeout und Archivpfade pruefen
