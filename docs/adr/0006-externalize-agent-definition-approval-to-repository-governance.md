# Externalize Agent Definition Approval to repository governance

Jede Änderung an einem Agent Definition Repository benötigt das Vier-Augen-Prinzip, wird aber nicht durch die Work Package Control Plane freigegeben. Das jeweilige Projekt erzwingt Agent Definition Approval über seine bestehende Repository Governance: geschützte Branches sowie Pull oder Merge Request mit menschlichem Code Review. GitHub, GitLab und Azure DevOps sind gleichwertige mögliche Provider. Die Work Package Control Plane und die Agent Evolution Loop dürfen nur eine Revision verwenden, die der jeweilige Provider bereits nach seinen konfigurierten Regeln als gemergt und freigegeben ausweist. Dadurch bleibt die organisatorische Code-Governance an ihrem bestehenden Ort und die Control Plane benötigt weder ein paralleles Rollenmodell noch eine eigene Nachbildung von Branch Protection.

## Consequences

- Autor und freigebender Reviewer müssen nach den Regeln des Repository Providers unterschiedliche menschliche Identitäten sein.
- Die Agent Evolution Loop darf Pull oder Merge Requests vorbereiten, aber weder Review noch Merge als menschliche Freigabe simulieren.
- Die Work Package Control Plane benötigt nur einen providerneutralen Vertrag für qualifizierte Agent-Definition-Revisionen; sie konfiguriert oder verwaltet keine Branch-Protection-Regeln.
- Tests der Control Plane beweisen, dass ungeprüfte Revisionen nicht verwendet werden und eine extern qualifizierte Revision verwendbar wird; sie testen nicht die internen Schutzmechanismen des Repository Providers erneut.
