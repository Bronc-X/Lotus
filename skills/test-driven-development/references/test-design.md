# Test design

Choose the lowest-cost test level that observes the required behavior:

- Unit tests for pure rules and transformations.
- Component or integration tests for boundaries between modules, storage, or services.
- Contract tests for external schemas and stable interfaces.
- End-to-end tests for critical user paths that cannot be proved more cheaply.

Test outcomes and public contracts rather than private call order or incidental structure. Include a boundary or failure case when it represents meaningful risk. Reuse existing fixtures and helpers; add new ones only when they reduce duplication without hiding the scenario.

For a bug, reproduce the reported failure in a test when the behavior is deterministic and maintainable. For legacy code, add a characterization test before changing behavior when the current contract is unclear.

Keep network, time, randomness, and external services controlled. If isolation would produce a misleading test, use an integration boundary and document the dependency.
