---
name: polanyi-tacit
description: 分析复杂代码中未明说的业务约束与隐性惯例。
---

# Polanyi tacit analysis

Identify behavior the code relies on but does not state explicitly.

Look for repeated exceptions, asymmetrical branches, sequencing, defensive checks, naming conventions, ownership boundaries, handoffs, and places where tests encode behavior more clearly than documentation.

For each useful finding, distinguish:

- evidence in code, tests, history, or runtime behavior;
- the likely hidden constraint;
- confidence and plausible alternatives;
- the risk of changing it;
- the cheapest way to verify it with a maintainer or observable test.

Do not turn speculation into fact or treat every unusual pattern as intentional. The output should help a reader change the code safely, not merely judge its style.
