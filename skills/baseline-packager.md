---
name: baseline-packager
description: 用户要求固化已验证行为时，创建可重复运行的回归基线。
risk: medium
source: lotus
date_added: "2026-05-11"
---

# Baseline Packager

Use only when the user explicitly invokes `/baseline-packager`.

This skill is for the moment after tests or manual verification have passed and before more changes begin. Its job is to package the current correct behavior into a baseline, golden master, or regression gate so later edits cannot silently break it.

It is not a loop controller. It does not run forever. It does not default to Playwright. Browser testing is only one possible protection method when the baseline is a browser user path.

## Workflow

1. **Confirm Baseline**
   - What behavior has already passed?
   - Is the protected surface a user path, business rule, API output, CLI output, install flow, generated artifact, or UI behavior?
   - What evidence proves it currently passes?
   - What is the current git state?

2. **Choose Protection**
   - Prefer existing project commands: build, test, lint, typecheck, existing scripts, existing CI.
   - If no check exists, add the smallest useful test, script, fixture, snapshot, or golden file.
   - Use Playwright only when the protected behavior is a browser path.
   - Protect user-observable behavior before implementation details.

3. **Package Entrypoint**
   - Create or confirm one command that can be run independently.
   - Preferred names:
     - `npm run test:baseline`
     - `npm run test:regression`
     - `npm run qa:baseline`
   - The command must exit non-zero on failure.

4. **Freeze the Rule**
   - Document the command in README, AGENTS.md, test docs, or project rules.
   - State that future changes must run the baseline before and after the change.
   - Suggest a git tag for important checkpoints, for example `baseline-YYYY-MM-DD-tested`.

5. **Verify**
   - Run the baseline command.
   - Run nearby existing checks when relevant.
   - If it fails, return to baseline definition. Do not force the test to pass.

## Output

Report:

- Baseline target
- Current passing evidence
- Protection method
- New or reused command
- Files changed
- Verification result
- Future-change rule

## Constraints

- Do not default to Playwright
- Do not refactor unrelated code
- Do not expand test scope beyond the baseline
- Do not write empty tests
- Do not confuse committed code with protected behavior
- Do not weaken assertions to preserve a broken baseline
