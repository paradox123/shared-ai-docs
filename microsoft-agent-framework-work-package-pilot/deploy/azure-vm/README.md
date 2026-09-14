# Azure Operator pilot

Deploys the accepted requirements intake GUI/API from GUI Ticket 01. It does
not start background workers or implement the later GUI tickets.

## Layout

Deployment endpoint: <https://wpcp-dh-3c8f1707.swedencentral.cloudapp.azure.com/operator/>.
VM: `wpcp-operator`; NSG: `wpcp-operator-sweden-nsg`; public IP resource:
`wpcp-operator-ip`. The dedicated local SSH key is
`~/.ssh/wpcp-operator-azure`; its paired `-known-hosts` file was populated from
the server's public host key retrieved through authenticated Azure Run Command.

One Ubuntu 24.04 VM runs Docker Compose: Caddy terminates public HTTPS and
forwards to the API on `127.0.0.1:5080`; PostgreSQL is published only on
`127.0.0.1:5432`. The API runs as the image's unprivileged `app` user with a
read-only root filesystem. The server holds no human GitHub credential;
authorization arrives from the browser for each request. Access/body logging
is disabled. Only ports 80/443 are publicly allowed; SSH is restricted to the
operator's current public `/32` address.

The named PostgreSQL and Caddy volumes live on the persistent managed OS disk.
Application replacement, Docker restart and VM deallocation preserve these
volumes. This single-VM pilot has no high availability or off-VM backup yet.
Never use `docker compose down --volumes` on the retained deployment.

## Subscription and cost

Use subscription `3c8f1707-52b9-43cc-9486-30faab0af3f0` (`Azure subscription 1`)
in tenant `3602223d-667f-4cff-a98a-6c4ecb75f18c`. Azure reported `FreeTrial` and
`spendingLimit: On` on 2026-09-14. The other signed-in subscription, Microsoft
Partner Network, reports PayAsYouGo and is not this deployment target.
Keep passing `--subscription` explicitly; never upgrade or remove the limit
as part of deployment. The remaining credit balance has not been established.

The selected VM is B2als v2 (2 vCPU, 4 GiB), with a 32 GiB Standard SSD and a
standard public IP in Sweden Central. North Europe rejected the initial B2s
request for lack of capacity. The Azure retail API returned USD 0.0389/hour
for this VM, USD 2.40/month for the disk, and USD 0.005/hour for the public IP
on 2026-09-14. Allow approximately USD 35/month
at continuous operation, plus actual network/disk operations and applicable
taxes; credit eligibility and remaining balance are account-specific.

The resource group is `rg-wpcp-operator-pilot` (metadata in North Europe, workload
in Sweden Central); it is separate from the existing
`rg-agent-framework-pilot` and its Durable Task scheduler. No resources from
that existing pilot are reconfigured.

## Build and configuration

Run from the application directory. The Dockerfile uses an allowlist context
and locked NuGet restore; it excludes runtime state, credentials and local
build products. Record the image ID alongside the source revision for each
release; a named release image is built once and retained for rollback.

```bash
docker build -f deploy/azure-vm/Dockerfile -t wpcp-operator:<release> .
```

Copy `compose.yaml` and `Caddyfile` to `/opt/wpcp/` on the VM. Copy the reviewed
`submission-config.example.json` to `/opt/wpcp/submission.json`; preserve the
existing logical repository binding. Configure any real redaction inventory
privately. Generate `/opt/wpcp/.env` on the VM with mode `0600`, containing:

```text
WPCP_HOSTNAME=<Azure public DNS name>
WPCP_API_IMAGE=wpcp-operator:<release>
WPCP_DATABASE_PASSWORD=<new random hex password>
```

Do not print `docker compose config` or container environment inspection with
real credentials. `docker compose config --quiet` validates without output.
`cloud-init.yaml` installs and enables Docker and Compose on Ubuntu 24.04;
wait for cloud-init completion separately from Azure VM provisioning.

Start the service on the VM:

```bash
cd /opt/wpcp
sudo docker compose config --quiet
sudo docker compose up -d
sudo docker compose ps
```

Open `https://<Azure public DNS name>/operator/` and authenticate with the
human's GitHub credential. See [SUBMISSIONS.md](../../SUBMISSIONS.md) for
permissions and source eligibility. A health response alone is not acceptance:
verify actual title/body, repository, stable ID, `admitted` and `runId: null`
through the GUI and public API before and after service replacement.

## Operations

Apply an already-built release by changing only `WPCP_API_IMAGE` in the private
environment file, then `sudo docker compose up -d --no-deps api`. Roll back
using the previous retained image tag and the same command. Preserve the
database password, submission configuration and named volumes.

For an explicit database backup, run on the server and transfer the private
backup to protected storage before deleting the server or disk:

```bash
cd /opt/wpcp
umask 077
sudo docker compose exec -T database pg_dump -U wpcp -d wpcp -Fc > wpcp-backup.dump
```

To pause/start compute from an authenticated Azure CLI:

```bash
az vm deallocate --subscription 3c8f1707-52b9-43cc-9486-30faab0af3f0 -g rg-wpcp-operator-pilot -n wpcp-operator
az vm start --subscription 3c8f1707-52b9-43cc-9486-30faab0af3f0 -g rg-wpcp-operator-pilot -n wpcp-operator
```

Deallocation stops compute charges; the retained disk and public IP can still
incur charges. Do not delete the resource group as a substitute for pausing.

Sources: [Azure spending limit](https://learn.microsoft.com/en-us/azure/cost-management-billing/manage/spending-limit),
[cloud-init](https://learn.microsoft.com/en-us/azure/virtual-machines/linux/using-cloud-init),
[Caddy automatic HTTPS](https://caddyserver.com/docs/automatic-https),
[Azure retail prices API](https://learn.microsoft.com/en-us/rest/api/cost-management/retail-prices/azure-retail-prices).
