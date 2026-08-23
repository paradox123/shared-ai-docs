## ADDED Requirements

### Requirement: Start the complete local stack in the user login domain
The operating package MUST install one user-specific macOS LaunchAgent that starts after Daniel logs in without root privileges or a manual process start. The managed stack MUST contain exactly one local `github-issue-pilot` process serving as both receiver and workflow worker and exactly one named `cloudflared` Tunnel process. Installation MUST be repeatable and MUST keep the LaunchAgent and its executable paths outside the repository working tree.

#### Scenario: User session loads the installed agent
- **WHEN** the LaunchAgent is installed or a later GUI login loads it
- **THEN** launchd starts one stack generation containing one loopback receiver/worker and one named Tunnel without a manual process command

#### Scenario: Installation is repeated
- **WHEN** the same user installs the same LaunchAgent configuration again
- **THEN** the existing user-domain job and installed supervisor are replaced safely without creating a second loaded job

### Requirement: Recover crashed managed processes through existing durable identities
The LaunchAgent MUST restart the managed stack after either child exits unexpectedly. A stack restart MUST reuse the same persistent database and operating-system boot identity so existing startup reconciliation, delivery-command deduplication, workflow recovery, and durable operation identities prevent another boot reconciliation, another workflow run, or duplicate external effects. A deliberate stop or uninstall MUST terminate both children without an automatic restart.

#### Scenario: Receiver or workflow worker crashes
- **WHEN** the managed pilot process exits unexpectedly after a delivery has been durably accepted
- **THEN** launchd starts a new stack generation, the pilot resumes the existing boot and workflow identities, and public read-back exposes one workflow effect for that delivery

#### Scenario: Tunnel crashes
- **WHEN** the managed Tunnel process exits unexpectedly
- **THEN** the supervisor stops the sibling pilot process and launchd starts one fresh stack generation with one Tunnel and one pilot process

#### Scenario: Operator stops the agent
- **WHEN** the operator explicitly stops or uninstalls the user LaunchAgent
- **THEN** both managed children terminate and launchd does not immediately recreate the unloaded job

### Requirement: Keep configuration and diagnostics local, private, bounded, and correlatable
The LaunchAgent plist and repository MUST contain no secrets, tokens, webhook bodies, issue or pull-request bodies, feedback, email addresses, or arbitrary child output. Runtime configuration MUST be read from an explicitly selected user-owned regular file outside the repository whose group and other permission bits are clear. Managed child stdout and stderr MUST NOT enter the lifecycle log. Local state and lifecycle diagnostics MUST contain only bounded timestamps, generation identifiers, service names, process identifiers, exit codes, readiness outcomes, and correlation-safe workflow identifiers, and MUST be private to the user.

#### Scenario: Private configuration fails safety checks
- **WHEN** the selected environment file is missing, not regular, not owned by the current user, or accessible by group or other users
- **THEN** validation fails before either managed child starts and reports only the failing safety category, not file contents or values

#### Scenario: Child emits sensitive material
- **WHEN** a managed child writes a token, payload, email address, or arbitrary exception to stdout or stderr
- **THEN** the LaunchAgent lifecycle log and supervisor state contain none of that child output

#### Scenario: Operator inspects local status
- **WHEN** the operator requests status for the installed LaunchAgent
- **THEN** the result correlates launchd job state, current stack generation, managed service PIDs, and loopback receiver readiness without displaying environment values or payload material

### Requirement: Restrict connectivity to loopback and the named outbound Tunnel
Managed operation MUST bind the receiver to `127.0.0.1`, MUST require an HTTPS public receiver URL whose path is exactly `/webhooks/github`, and MUST validate the selected named Tunnel configuration and exact route before starting the stack. Installation and runtime MUST NOT open router or firewall ingress, bind the receiver to a public interface, create a system LaunchDaemon, or place Cloudflare Access before the machine endpoint. The Tunnel configuration MUST retain a final `404` catch-all so no other local route is published.

#### Scenario: Valid outbound-only configuration starts
- **WHEN** a private configuration names existing absolute executables, a valid named Tunnel configuration, an HTTPS `/webhooks/github` URL, and a bounded local port
- **THEN** the receiver listens only on loopback and `cloudflared` establishes the public path with outbound connections

#### Scenario: Unsafe receiver or Tunnel configuration is supplied
- **WHEN** the receiver host is non-loopback, the public URL is not HTTPS or has another path, or Tunnel validation/routing fails
- **THEN** startup fails before the receiver or Tunnel child is launched

### Requirement: Document and prove bounded unattended operation
Operating guidance MUST document installation, configuration, start, status, logs, explicit restart, uninstall, the Cloudflare Free Queue's 24-hour retention boundary, once-per-boot startup reconciliation, local workflow and relay diagnostic surfaces, and every human step that remains outside automation. Acceptance evidence MUST include a start proof and a recovery proof through the installed LaunchAgent/supervisor boundary, signed HTTP acceptance, real SQLite persistence, and public workflow read-back; logs alone MUST NOT be considered proof of workflow behavior.

#### Scenario: Clean managed start processes a delivery
- **WHEN** the installed user LaunchAgent starts a controlled stack generation and receives a valid signed delivery
- **THEN** signed HTTP acceptance and workflow read-back prove that the delivery reached one durable workflow without a manual process start

#### Scenario: Managed crash recovery remains exact once
- **WHEN** acceptance terminates one managed process, waits for a new launchd generation in the same boot, and resubmits the same signed delivery
- **THEN** HTTP acknowledgement, public read-back, and controlled external effects prove one recovered workflow and no duplicate processing

#### Scenario: Mac absence exceeds free retention
- **WHEN** operating guidance describes a Mac outage of at least 24 hours
- **THEN** it states that Queue delivery is no longer guaranteed, startup reconciliation runs at most once for the new boot, and manual GitHub/DLQ investigation can still be required
