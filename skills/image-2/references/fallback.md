# Authorized API fallback
Use only when native image tools are unavailable and the user has authorized this endpoint, cost, and data transfer.
The bundled `scripts/image2_newapi.py` supports generation and batch generation, not arbitrary reference-image edits. Run its help from the skill directory for current arguments.
Keep credentials in environment variables or ignored `runtime.local.json`; `runtime.example.json` is only a template. Prefer environment/config over command-line secrets.
Configuration precedence: explicit arguments, IMAGE2_NEWAPI_KEY / IMAGE2_NEWAPI_BASE_URL, then runtime.local.json.
Example, from the skill directory:
```text
python scripts/image2_newapi.py generate --prompt "..." --out <output.png> --size 1024x1024 --quality low
python scripts/image2_newapi.py generate-batch --input <prompts.jsonl> --out-dir <output-directory>
```
Batch JSONL items may contain prompt, out, size, and quality. Select quality and batch size for the requested output; do not silently trade away quality or initiate unbounded paid retries.
Report service failures without credentials. If the request needs unsupported editing or alpha output, state the limitation and use a supported authorized path rather than claiming equivalence.
