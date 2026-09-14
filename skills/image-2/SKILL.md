---
name: image-2
description: 用户要求 GPT Image 2 位图生成、参考图变体或图片编辑时使用。
---

# Image 2
Produce the requested image, not merely a prompt, unless the user asks for prompts.
Use the native image-generation/editing tool when available and follow its current input, reference-image, and output contract. The system imagegen skill is the source for host-specific mechanics.
If the native tool is unavailable, read [references/fallback.md](references/fallback.md) only when using a configured, authorized API fallback. A missing native tool does not authorize new credentials, paid calls, or uploading private reference images.
Preserve the requested subject, text, composition, identity, and edit scope. Use reference images through the tool's supported mechanism. Check actual capability support rather than assuming transparency, editing, or model selection works identically across providers.
Inspect the generated result for the requested constraints. Correct concrete failures within the authorized scope and budget. Save project assets where the project can use them; do not overwrite existing files unless replacement was requested.
