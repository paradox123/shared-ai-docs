## 1. Change and Test Harness

- [x] 1.1 Strictly validate the active OpenSpec change before implementing runtime behavior.
- [x] 1.2 Create the isolated Worker package, locked toolchain, generated binding types, Workers Vitest harness, and ignored local runtime state without adding production behavior.

## 2. Vertical Behavior Slices

- [x] 2.1 Add a failing Worker-handler test for valid signed ingress, then implement bounded raw authentication, allowlisting, one awaited Queue publication, and post-persistence `202`.
- [x] 2.2 Add failing Worker-handler tests for invalid method/path/body/signature/delivery/repository/event/action and Queue failure, then implement reasoned effect-free rejection.
- [x] 2.3 Add failing local HTTP tests for relay-signature acceptance, tampering, ambiguous configuration, and shared canonical HMAC examples, then implement mutually exclusive direct and relay authentication modes.
- [x] 2.4 Add failing Queue-handler tests for separately signed exact-path delivery, durable acceptance acknowledgement, duplicate acceptance, and mismatched responses, then implement the consumer contract and secret-free logging.
- [x] 2.5 Add failing behavior/configuration tests for retry backoff, unsafe receiver URLs, finite retry limits, and the named dead-letter queue, then implement retry handling and deployable Wrangler configuration.
- [x] 2.6 Add a duplicate relay system test through the productive local HTTP/read-model seams, then add the named Tunnel example and operating guidance for outbound-only routing, exact-path exposure, separate secrets, free-plan retention, and DLQ inspection.

## 3. Verification and Closeout

- [x] 3.1 Refactor the touched Worker, local receiver, tests, specs, and docs for DRY, SOLID, and KISS issues while preserving behavior.
- [x] 3.2 Run Worker type generation/checking, lint, contract tests, Wrangler dry-run/config validation, Python lint/tests, dependency audits, `git diff --check`, and strict OpenSpec validation.
- [x] 3.3 Record criterion-by-criterion implementation evidence and update local issue 09 only for directly verified acceptance criteria.
