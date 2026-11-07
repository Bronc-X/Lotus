# Authorized API fallback
Use when native image tools are unavailable or cannot select the explicitly requested model, and the user has authorized this endpoint, cost, and data transfer.
The bundled `scripts/image2_newapi.py` supports generation and batch generation, not arbitrary reference-image edits. It defaults to `gpt-image-2.5-sunburst`; use `--model gpt-image-2.5-flare` for faster everyday generation, or retain another model only when explicitly requested. Run its help from the skill directory for current arguments. Verify the third-party provider actually exposes the selected model before claiming a successful 2.5 migration.
Keep credentials in environment variables or ignored `runtime.local.json`; `runtime.example.json` is only a template. Prefer environment/config over command-line secrets.
Configuration precedence: explicit arguments, IMAGE2_NEWAPI_KEY / IMAGE2_NEWAPI_BASE_URL, then runtime.local.json. `model` can be set with `--model` or `runtime.local.json`; an existing local model pin overrides the default.
Example, from the skill directory:
```text
python scripts/image2_newapi.py generate --prompt "..." --out <output.png> --size 1024x1024 --quality low
python scripts/image2_newapi.py generate-batch --input <prompts.jsonl> --out-dir <output-directory>
```
Batch JSONL items may contain prompt, out, size, and quality. Select quality and batch size for the requested output; do not silently trade away quality or initiate unbounded paid retries.
Report service failures without credentials. If the request needs unsupported editing or alpha output, state the limitation and use a supported authorized path rather than claiming equivalence.
