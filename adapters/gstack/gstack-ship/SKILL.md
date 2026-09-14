---
name: ship
description: 执行用户明确要求的提交、推送、PR 或版本交付步骤。
---

# Scoped code delivery
Deliver only the requested Git/release outcome. “The code is ready” alone does not authorize a push, PR, merge, or deployment.
## Local preparation
Inspect the checkout, branch, remote, status, and diff. Keep user changes separate; stage only intended paths. Run existing checks appropriate to the change and inspect failures before proceeding.
For a commit-only request, stop after the verified commit. Do not automatically create a release, change VERSION/CHANGELOG, or run every review skill.
## Remote operations
For an authorized push, verify the destination branch and use a normal non-force push. Confirm remote state afterward.
For a PR, use the requested base and scope, include verification evidence, and verify the resulting PR. Creating a PR does not authorize merging it.
For a release or deployment, read the project's release/deployment instructions and execute only the explicitly authorized environment and actions.
Do not automatically merge/rebase unrelated changes, bypass protections, force-push, publish packages, purchase services, or modify production.
If a required check or remote operation fails, fix in-scope failures and recheck, or report the precise blocker. Do not claim delivery merely because a local commit exists.
