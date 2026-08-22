## MODIFIED Requirements

### Requirement: Authenticate and authorize local GitHub deliveries
The local workflow interface MUST accept only bounded requests using its configured authentication mode: either a valid GitHub `X-Hub-Signature-256` over the unchanged raw body or a valid internal `X-Pilot-Signature-256` over the delivery ID, event, and unchanged raw body. It MUST require a non-empty `X-GitHub-Delivery`, the configured repository, and an explicitly allowed event/action combination, and MUST verify the configured signature before parsing JSON. GitHub and internal relay secrets MUST be configured separately and an application instance MUST NOT accept both authentication modes simultaneously.

#### Scenario: Allowed directly signed delivery
- **WHEN** a correctly GitHub-signed `issues/labeled` delivery for the configured `probare-crm` repository arrives within the request-size limit in direct mode
- **THEN** the interface accepts the delivery for durable processing

#### Scenario: Allowed relay-signed delivery
- **WHEN** a correctly internally signed `issues/labeled` delivery with bound delivery ID and event for the configured `probare-crm` repository arrives within the request-size limit in relay mode
- **THEN** the same productive interface accepts the delivery for durable processing

#### Scenario: Invalid or unauthorized delivery
- **WHEN** a delivery has an invalid configured signature, exceeds the request-size limit, targets a non-allowed repository, or uses a non-allowed event/action combination
- **THEN** the interface rejects it without an inbox record, a workflow run, or a GitHub write

#### Scenario: Ambiguous authentication configuration
- **WHEN** an application instance is configured with both GitHub and internal relay secrets or with neither secret
- **THEN** application construction fails before serving requests
