# Focused security review

Select only the trust surfaces implicated by the requested review. A narrow audit does not require a new monitoring system, CI pipeline, compliance program, or developer training.

## Evidence and scope
Identify the assets, actors, entry points, privileges, and deployment boundaries from available code and configuration. Ask only for material missing facts that cannot be verified safely.
Trace the relevant input through middleware, privileged services and storage. Verify middleware actually executes: filenames, exports and route matchers can bypass intended checks.
For each finding, state the code location, attacker preconditions, exploit path, impact, confidence, and remediation. Separate a suspicious pattern from a demonstrated vulnerability.

## Relevant checks
- Authorization: enforce object and tenant ownership on reads and mutations, including paths using privileged SDKs that bypass database policies.
- Authentication: check session/token validation, issuer/audience, expiry, revocation and key handling as applicable.
- Input/output: parameterize queries, validate structured inputs and safely encode output; identify unsafe deserialization and injection sinks.
- Network boundaries: for SSRF, inspect allowed destinations, resolution, redirects and address validation; avoid testing private or production endpoints without authorization.
- Secrets/data: check storage, logs, generated artifacts, permissions and retention for unintended disclosure.
- Supply chain: examine affected manifests, lockfiles, provenance and current advisories; a package name alone is not evidence of exploitability.
- Infrastructure: review only relevant exposed services, identity grants and deployment configuration.
- Agent systems: distinguish retrieved data from instructions; bind external writes to user authority and scope.

## Validation and limits
Use static inspection or isolated test fixtures by default. Intrusive testing, production effects, credential rotation and access changes need explicit authorization.
A review is read-only unless remediation is requested. For fixes, apply the smallest effective change and rerun affected security and regression checks.
Do not output secrets or sensitive records. Use current authoritative standards when a specific compliance assessment requires them; do not claim certification or legal compliance from this checklist.
