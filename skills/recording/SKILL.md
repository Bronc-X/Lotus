---
name: recording
description: 将录音整理为可追溯内容母库，并制作用户选定的内容资产。
---

# Recording

Build derivatives from a traceable content library, not directly from an unverified transcript.

## Route the request

Read only the references needed for the current stage:

- Ingest, transcription, timing, speaker identity, rights, restricted segments, or library construction: [references/core-workflow.md](references/core-workflow.md).
- Choosing or tracking output branches: [references/asset-planning.md](references/asset-planning.md).
- Producing a selected asset: [podcast](references/podcast.md), [article](references/article.md), [video](references/video.md), [social](references/social.md), [knowledge](references/knowledge.md), or [commercial](references/commercial.md).
- Uploading, publishing, or distribution verification: [references/publishing.md](references/publishing.md), in addition to the selected asset reference.

Do not load every branch guide. If the request is only audio cleanup, trimming, transcoding, device setup, live voice, or ordinary copy editing without recording evidence, this workflow does not apply.

For a fully synthesized single-host episode from documents or an approved script, use `ai-podcast` directly when available. A short human recording used only as a voice reference does not require a Recording content-library project.

## Invariants

- Treat the only copy of an original recording as read-only. Record its size and SHA-256 before processing; derived audio belongs in a work directory.
- Do not process active, growing, partial, or undecodable recordings.
- Evidence must remain traceable to `source_id + track + source_time + source_sha256`. Preserve ambiguity, overlap, conflicting numbers, and identity uncertainty instead of guessing.
- Unconfirmed people stay anonymous and evidence-only. Text quotation, original audio, voice sampling, synthesis, avatar use, upload, and public release are separate permissions.
- Restricted `EXISTENCE_ONLY` segments may record existence and range only; do not transcribe, summarize, embed, label, or leak them through filenames.
- “Continue” advances only the selected branch and already-authorized step. It does not add assets, accounts, uploads, or publication rights.
- Before any public write, freeze a release candidate and verify that existing user authorization covers its content, platform, account and action. Record the actual candidate hashes with that evidence. Reuse matching authorization; ask only when the current candidate or target is not covered. Never invent an approval event or infer public rights from local production alone.

## Entry points

Create a project only when recording work is actually in scope:

```powershell
pwsh -NoProfile -File scripts/new_recording_project.ps1 `
  -ProjectId <project-id> `
  -Title <title> `
  -Destination <absolute-project-path> `
  -BrandProfile <Blank|DeepEvolutions>
```

Use `powershell` instead of `pwsh` on Windows PowerShell 5.1. The script refuses to overwrite an existing directory.

Validate the current project stage with:

```powershell
pwsh -NoProfile -File scripts/qa_recording_project.ps1 -ProjectRoot <absolute-project-path>
```

Completion for the selected stage means the requested assets exist, their evidence and permissions pass the relevant checks, failures have been corrected and rechecked, and every ungranted external action remains blocked.
