# Azure deployment — 2026-09-14

The accepted Ticket 01 requirements intake is deployed at
[the Azure Operator GUI](https://wpcp-dh-3c8f1707.swedencentral.cloudapp.azure.com/operator/).
The server is an Ubuntu 24.04 B2als v2 VM in Sweden Central, with its own
PostgreSQL database. The operator browser ran on the local Mac over public
HTTPS. The request was deployment before the wider distributed acceptance;
remaining Ticket 16 scenarios stay open.

| Expected | Observed | Evidence |
| --- | --- | --- |
| Reach the actual GUI securely from the Mac | Validated public TLS, HTTP 200, “Anforderungen”, no-store and CSP/HSTS headers; rendered desktop and mobile without browser errors or horizontal overflow. | [Desktop](evidence/azure-deployment/desktop.png), [mobile](evidence/azure-deployment/mobile.png), [browser record](evidence/azure-deployment/browser-smoke.json). |
| Admit real provider content into the empty deployment | GitHub `paradox123/probare-crm#4` appeared with its real title/body/repository; repeated GUI delivery retained one record, `state=admitted`, `runId=null`. No GitHub writes or agent execution. | [Browser record](evidence/azure-deployment/browser-smoke.json). |
| Retain the admitted version independently of service containers and browser | Recreated both API and database containers, then authenticated in a fresh Chrome process. Public readback matched the complete original snapshot, including identity and admitted content. | [Browser record](evidence/azure-deployment/browser-smoke.json); ID `23d2e174-1cd7-4cb1-94f7-32bf41dfa54d`. |
| Keep stored input protected | Anonymous overview and detail both returned 401. API and database listeners are loopback-only; SSH is restricted to the operator's `/32`. The server-generated database environment file is `0600 root:root`. | [Deployment inventory](evidence/azure-deployment/deployment.json); browser record. |
| Use the credit subscription without removing its limit | Azure reported an enabled FreeTrial subscription and spending limit On, including after provisioning. The existing Durable Task scheduler remains in its original resource group. | [Deployment inventory](evidence/azure-deployment/deployment.json), [operations guide](../../../../microsoft-agent-framework-work-package-pilot/deploy/azure-vm/README.md). |

The application image uses source baseline `39038d3` and the recorded source
archive SHA-256; application code did not change. Its runtime image ID is
`sha256:f5ac954f10879f3d918098d199386fe98a9bd4a5d5200d939473fc37eb0bd7a5`.
The new deployment assets pin their .NET, PostgreSQL and Caddy base images by
digest and send only the allowlisted application source to Azure. Human GitHub
credentials reach the API only in HTTPS requests, never through the deployment
archive, server configuration or retained proof.

Checks: local Linux container build and published GUI/API assets; unprivileged
runtime user; Compose configuration; Caddy configuration; native x64 build on
Azure; live browser/API smoke and container replacement/readback; visual
inspection of desktop/mobile evidence; strict OpenSpec validation and diff
whitespace checks. An initial OpenSpec invocation from the application directory
was corrected to the owning repository root. No application regression suite
was repeated for deployment-only configuration changes.

The first North Europe B2s allocation failed capacity validation. Azure's
subscription-specific SKU API showed Sweden Central availability, and the
replacement deployment succeeded there. The unused North Europe NSG created
by this task was removed; no failed VM, public IP or disk remained there.

Limitations: approximately USD 35/month at continuous operation before extra
usage/taxes, drawn against eligible credit while it lasts; remaining credit
balance is not established. This is a single VM with persistent local volumes,
without high availability or an off-VM backup yet. Whole-VM recovery, other
human identities, revoked permissions under this deployment, full distributed
handover/history and autonomous execution were not claimed by this smoke proof.
