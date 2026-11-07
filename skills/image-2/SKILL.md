---
name: image-2
description: 用户要求 GPT Image 2.5 或 Image 2 位图生成、参考图变体或图片编辑时使用。
---

# Image 2.5 / Image 2
Produce the requested image, not merely a prompt, unless the user asks for prompts.
Use the native image-generation/editing tool when available and follow its current input, reference-image, and output contract. The system imagegen skill is the source for host-specific mechanics.
When the user specifically requests Image 2.5, check whether the native tool actually exposes that model or a model selector. Do not label a native Image 2 result as Image 2.5. If the native path cannot select 2.5, use a configured, authorized API path or state the limitation.
For the third-party newapi path, read [references/fallback.md](references/fallback.md). Its default model is `gpt-image-2.5-sunburst`; choose `gpt-image-2.5-flare` explicitly when speed is the priority. A missing native tool or an unavailable model does not authorize new credentials, paid calls, or uploading private reference images.
Preserve the requested subject, text, composition, identity, and edit scope. Use reference images through the tool's supported mechanism. Check actual capability support rather than assuming transparency, editing, or model selection works identically across providers.
Inspect the generated result for the requested constraints. Correct concrete failures within the authorized scope and budget. Save project assets where the project can use them; do not overwrite existing files unless replacement was requested.
