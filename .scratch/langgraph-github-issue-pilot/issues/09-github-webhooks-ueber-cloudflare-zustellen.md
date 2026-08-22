# 09: GitHub-Webhooks 24 Stunden ueber Cloudflare zustellen

**What to build:** GitHub-Ereignisse erreichen den lokalen Receiver auch waehrend kurzer Mac-Ausfaelle ueber einen signierten Cloudflare-Ingress, eine kostenlose 24-Stunden-Queue und einen ausgehend aufgebauten Tunnel.

**Blocked by:** 01: Ein autorisiertes Issue lokal annehmen und claimen

**Covers:** US 13-22, 57, 68

**Status:** ready-for-agent

- [x] Vor der Implementierung beschreibt ein kleiner aktiver OpenSpec-Change Ziel, Scope, Write-Set und direkte Verifikation dieses Slices und besteht die strikte Validierung.
- [x] Der Edge-Ingress prueft die rohe GitHub-Signatur sowie Repository, Event und Action und schreibt eine gueltige Delivery genau einmal dauerhaft in die Queue, bevor er Erfolg bestaetigt.
- [x] Ungueltige Signaturen, nicht erlaubte Ereignisse und unzulaessige Repositories werden begruendet und ohne Queue-Wirkung abgelehnt.
- [x] Die Queue verwendet den kostenlosen Cloudflare-Tarif mit dem bewusst akzeptierten garantierten Retention-Fenster von 24 Stunden und behaelt `X-GitHub-Delivery` als durchgaengigen Idempotenzschluessel bei.
- [x] Der Consumer liefert ueber einen benannten, ausgehend aufgebauten Cloudflare Tunnel an genau den lokalen Webhook-Pfad; es werden keine Router-Ports geoeffnet und Cloudflare Access liegt nicht vor diesem Maschinenpfad.
- [x] Der zweite Hop ist separat signiert; GitHub- und interne Secrets werden getrennt gespeichert und weder Payloads noch Logs oder Evidence geben sie preis.
- [x] Eine Queue-Nachricht wird erst nach dauerhafter lokaler Annahme bestaetigt; temporaere Fehler werden mit Backoff wiederholt und dauerhaft fehlgeschlagene Nachrichten landen nach dem Versuchslimit sichtbar in der Dead-Letter-Behandlung.
- [x] Contract- und Systemtests beweisen Annahme, Ablehnung, Retry, Dead Letter und die deduplizierte Zustellung bis zum lokalen Claim ueber die vorgesehenen oeffentlichen Seams.
