#!/usr/bin/env python3
"""Local newapi fallback for the Lotus image-2 skill.

Reads API settings from runtime.local.json or IMAGE2_NEWAPI_* env vars and calls
an OpenAI-compatible Images API with GPT Image 2.5 Sunburst by default.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
from pathlib import Path
import ssl
import sys
import time
from typing import Any
from urllib import error, request

DEFAULT_MODEL = "gpt-image-2.5-sunburst"
DEFAULT_SIZE = "1024x1024"
DEFAULT_QUALITY = "low"
DEFAULT_FORMAT = "png"


def die(message: str, code: int = 1) -> None:
    print(f"Error: {message}", file=sys.stderr)
    raise SystemExit(code)


def skill_dir() -> Path:
    return Path(__file__).resolve().parents[1]


def load_runtime(path: str | None) -> dict[str, Any]:
    candidates: list[Path] = []
    if path:
        candidates.append(Path(path))
    candidates.append(skill_dir() / "runtime.local.json")

    for candidate in candidates:
        if candidate.exists():
            return json.loads(candidate.read_text(encoding="utf-8"))
    return {}


def runtime_value(args: argparse.Namespace, config: dict[str, Any], key: str, env: str) -> str | None:
    value = getattr(args, key.replace("-", "_"), None)
    if value:
        return value
    value = os.getenv(env)
    if value:
        return value
    raw = config.get(key) or config.get(key.replace("-", "_"))
    return str(raw) if raw else None


def endpoint(base_url: str) -> str:
    base = base_url.rstrip("/")
    if base.endswith("/v1"):
        return f"{base}/images/generations"
    return f"{base}/v1/images/generations"


def ssl_context() -> ssl.SSLContext:
    try:
        import certifi  # type: ignore[import-not-found]

        return ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        return ssl.create_default_context()


def request_json(url: str, api_key: str, payload: dict[str, Any], timeout: int) -> dict[str, Any]:
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = request.Request(
        url,
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=timeout, context=ssl_context()) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        die(f"HTTP {exc.code} from image API: {detail}")
    except error.URLError as exc:
        reason = exc.reason
        if isinstance(reason, FileNotFoundError):
            die(f"Image API TLS setup failed: {reason}. Install certifi or set SSL_CERT_FILE to a valid CA bundle.")
        die(f"Image API request failed: {reason!r}")
    except FileNotFoundError as exc:
        die(f"Image API TLS setup failed: {exc}. Install certifi or set SSL_CERT_FILE to a valid CA bundle.")


def decode_image(item: dict[str, Any]) -> bytes:
    b64 = item.get("b64_json")
    if b64:
        return base64.b64decode(b64)
    url = item.get("url")
    if url:
        with request.urlopen(url, timeout=120, context=ssl_context()) as resp:
            return resp.read()
    die("Image API response did not contain b64_json or url.")
    return b""


def write_images(data: list[dict[str, Any]], out: Path, force: bool) -> list[Path]:
    out.parent.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    multiple = len(data) > 1

    for idx, item in enumerate(data, start=1):
        target = out
        if multiple:
            target = out.with_name(f"{out.stem}-{idx}{out.suffix}")
        if target.exists() and not force:
            die(f"Output already exists: {target} (use --force to overwrite)")
        target.write_bytes(decode_image(item))
        paths.append(target)
        print(f"Wrote {target}")
    return paths


def build_payload(args: argparse.Namespace, config: dict[str, Any], prompt: str) -> dict[str, Any]:
    model = args.model or config.get("model") or DEFAULT_MODEL
    payload: dict[str, Any] = {
        "model": model,
        "prompt": prompt,
        "size": args.size,
        "quality": args.quality,
        "n": args.n,
        "output_format": args.output_format,
    }
    return {k: v for k, v in payload.items() if v is not None}


def read_prompt(args: argparse.Namespace) -> str:
    if args.prompt and args.prompt_file:
        die("Use --prompt or --prompt-file, not both.")
    if args.prompt_file:
        return Path(args.prompt_file).read_text(encoding="utf-8").strip()
    if args.prompt:
        return args.prompt.strip()
    die("Missing prompt.")
    return ""


def generate(args: argparse.Namespace) -> None:
    config = load_runtime(args.runtime)
    base_url = runtime_value(args, config, "url", "IMAGE2_NEWAPI_BASE_URL")
    api_key = runtime_value(args, config, "key", "IMAGE2_NEWAPI_KEY")
    if not base_url:
        die("Missing newapi url. Set IMAGE2_NEWAPI_BASE_URL or runtime.local.json.")
    if not api_key or api_key == "set-your-own-key-locally":
        die("Missing newapi key. Set IMAGE2_NEWAPI_KEY or runtime.local.json.")

    prompt = read_prompt(args)
    payload = build_payload(args, config, prompt)
    out = Path(args.out)

    if args.dry_run:
        preview = dict(payload)
        preview["prompt"] = prompt
        print(json.dumps({"endpoint": endpoint(base_url), "payload": preview, "out": str(out)}, ensure_ascii=False, indent=2))
        return

    print(f"Calling newapi Image API with {payload['model']}.", file=sys.stderr)
    started = time.time()
    result = request_json(endpoint(base_url), api_key, payload, args.timeout)
    elapsed = time.time() - started
    print(f"Image API completed in {elapsed:.1f}s.", file=sys.stderr)

    data = result.get("data")
    if not isinstance(data, list) or not data:
        die(f"Unexpected image API response: {json.dumps(result, ensure_ascii=False)[:1000]}")
    write_images(data, out, args.force)


def generate_batch(args: argparse.Namespace) -> None:
    config = load_runtime(args.runtime)
    base_url = runtime_value(args, config, "url", "IMAGE2_NEWAPI_BASE_URL")
    api_key = runtime_value(args, config, "key", "IMAGE2_NEWAPI_KEY")
    if not base_url:
        die("Missing newapi url. Set IMAGE2_NEWAPI_BASE_URL or runtime.local.json.")
    if not api_key or api_key == "set-your-own-key-locally":
        die("Missing newapi key. Set IMAGE2_NEWAPI_KEY or runtime.local.json.")

    in_path = Path(args.input)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    lines = [line.strip() for line in in_path.read_text(encoding="utf-8").splitlines()]
    jobs = [json.loads(line) if line.startswith("{") else {"prompt": line} for line in lines if line and not line.startswith("#")]
    if not jobs:
        die("No jobs found.")

    for idx, job in enumerate(jobs, start=1):
        prompt = str(job.get("prompt", "")).strip()
        if not prompt:
            die(f"Missing prompt in job {idx}.")
        local = argparse.Namespace(**vars(args))
        local.prompt = prompt
        local.prompt_file = None
        local.model = job.get("model", args.model)
        local.size = job.get("size", args.size)
        local.quality = job.get("quality", args.quality)
        local.n = int(job.get("n", args.n))
        local.output_format = job.get("output_format", args.output_format)
        out_name = job.get("out") or f"{idx:03d}.png"
        local.out = str(out_dir / out_name)
        payload = build_payload(local, config, prompt)
        if args.dry_run:
            print(json.dumps({"endpoint": endpoint(base_url), "payload": payload, "out": local.out}, ensure_ascii=False))
            continue
        print(f"[{idx}/{len(jobs)}] Calling newapi Image API.", file=sys.stderr)
        result = request_json(endpoint(base_url), api_key, payload, args.timeout)
        data = result.get("data")
        if not isinstance(data, list) or not data:
            die(f"Unexpected response for job {idx}: {json.dumps(result, ensure_ascii=False)[:1000]}")
        write_images(data, Path(local.out), args.force)


def add_common(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--runtime", help="Path to runtime.local.json")
    parser.add_argument("--url", help="newapi base URL, for example https://aicanapi.com")
    parser.add_argument("--key", help="newapi API key")
    parser.add_argument("--model")
    parser.add_argument("--size", default=DEFAULT_SIZE)
    parser.add_argument("--quality", default=DEFAULT_QUALITY)
    parser.add_argument("--n", type=int, default=1)
    parser.add_argument("--output-format", default=DEFAULT_FORMAT)
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--dry-run", action="store_true")


def main() -> int:
    parser = argparse.ArgumentParser(description="image-2 newapi fallback for GPT Image 2.5")
    sub = parser.add_subparsers(dest="command", required=True)

    gen = sub.add_parser("generate")
    add_common(gen)
    gen.add_argument("--prompt")
    gen.add_argument("--prompt-file")
    gen.add_argument("--out", required=True)
    gen.set_defaults(func=generate)

    batch = sub.add_parser("generate-batch")
    add_common(batch)
    batch.add_argument("--input", required=True)
    batch.add_argument("--out-dir", required=True)
    batch.set_defaults(func=generate_batch)

    args = parser.parse_args()
    if args.n < 1 or args.n > 10:
        die("--n must be between 1 and 10")
    args.func(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
