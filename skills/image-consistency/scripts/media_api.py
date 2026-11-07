"""Portable, single-attempt image API adapter (Python 3.10+, Pillow).

Paid operations read ONLY MEDIA_API_BASE_URL and MEDIA_API_KEY.
The base URL includes the provider's version prefix, for example /v1.
No personal application config, credential files or provider SDK is consulted.
Recovery requires neither API credential nor paid submission.

Examples (configure the environment in the caller; never put secrets in argv):
  python media_api.py models
  python media_api.py generate --model MODEL --prompt-file prompt.txt --output out/card.png
  python media_api.py edit --model MODEL --prompt-file prompt.txt --reference person.png \
      --reference product.png --output out/look.png --params-file compatible.json
  python media_api.py recover --output out/look.png

Each paid command reserves a new *.receipt.json before sending one POST. A
pre-existing receipt or image prevents submission. UNKNOWN must be reconciled
with the provider before a human decides whether to create a new attempt.
Recover reads a private result capsule and never sends a paid POST.
Model strings are provider identifiers, not claims of official model support.
Video submission is intentionally absent pending a verified provider protocol.
"""

from __future__ import annotations

import argparse
import base64
import binascii
import ctypes
from dataclasses import dataclass, field
from datetime import datetime, timezone
import hashlib
import http.client
import io
import json
import math
import os
from pathlib import Path
import re
import socket
import stat
import tempfile
from typing import Any, Mapping
from urllib import error, parse, request
import uuid
import warnings


MAX_IMAGE_BYTES = 40 * 1024 * 1024
MAX_JSON_BYTES = 64 * 1024 * 1024
MAX_REFERENCES = 16
MAX_RECOVERY_BYTES = MAX_JSON_BYTES + 1024 * 1024
IMAGE_FORMATS = {"PNG": (".png", "image/png"), "JPEG": (".jpg", "image/jpeg"),
                 "WEBP": (".webp", "image/webp")}
PROTECTED_PARAMS = {"model", "prompt", "image", "image[]", "images", "n",
                    "authorization", "api_key", "apikey", "base_url", "headers"}


class MediaError(Exception):
    """Public exception text is fixed and contains no remote response or URL."""

    def __init__(self, code: str, message: str, outcome: str = "NOT_SUBMITTED",
                 http_status: int | None = None):
        super().__init__(message)
        self.code = code
        self.outcome = outcome
        self.http_status = http_status
        self.receipt_update_failed = False

    def safe_dict(self) -> dict[str, Any]:
        value = {"code": self.code, "message": str(self), "outcome": self.outcome}
        if self.http_status is not None:
            value["http_status"] = self.http_status
        if self.receipt_update_failed:
            value["receipt_update_failed"] = True
        return value


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _validated_url(value: str, allow_loopback_http: bool) -> str:
    try:
        parsed = parse.urlsplit(value)
        if any(ord(char) < 33 for char in value) or parsed.username or parsed.password:
            raise ValueError()
        if not parsed.hostname or parsed.fragment:
            raise ValueError()
        parsed.port  # Validate the port without displaying the URL on failure.
        loopback = parsed.hostname.lower() in {"localhost", "127.0.0.1", "::1"}
        if parsed.scheme != "https" and not (
                allow_loopback_http and loopback and parsed.scheme == "http"):
            raise ValueError()
    except (ValueError, TypeError, AttributeError):
        raise MediaError("INVALID_URL", "An HTTPS URL without user information is required.") from None
    return value


@dataclass(repr=False)
class Config:
    base_url: str = field(repr=False)
    api_key: str = field(repr=False)
    timeout: float = 300.0
    allow_loopback_http: bool = False

    @classmethod
    def from_env(cls, environ: Mapping[str, str] | None = None,
                 timeout: float = 300.0) -> "Config":
        env = os.environ if environ is None else environ
        base_url = env.get("MEDIA_API_BASE_URL", "").strip().rstrip("/")
        api_key = env.get("MEDIA_API_KEY", "").strip()
        if not base_url or not api_key:
            raise MediaError("CONFIG_MISSING", "Set MEDIA_API_BASE_URL and MEDIA_API_KEY in the environment.")
        if any(ord(char) < 33 or ord(char) > 126 for char in api_key):
            raise MediaError("INVALID_KEY", "The API key must be a single ASCII token.")
        allow_http = env.get("MEDIA_API_ALLOW_LOOPBACK_HTTP") == "1"
        _validated_url(base_url, allow_http)
        if parse.urlsplit(base_url).query:
            raise MediaError("INVALID_BASE_URL", "The API base URL must not include a query string.")
        if not math.isfinite(timeout) or timeout <= 0:
            raise MediaError("INVALID_TIMEOUT", "Timeout must be a positive finite number.")
        return cls(base_url, api_key, timeout, allow_http)

    @classmethod
    def for_recovery(cls, environ: Mapping[str, str] | None = None,
                     timeout: float = 300.0) -> "Config":
        """A saved result can be downloaded without an API key or another POST."""
        if not math.isfinite(timeout) or timeout <= 0:
            raise MediaError("INVALID_TIMEOUT", "Timeout must be a positive finite number.")
        env = os.environ if environ is None else environ
        return cls("", "", timeout, env.get("MEDIA_API_ALLOW_LOOPBACK_HTTP") == "1")


class _NoRedirect(request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        # Redirecting a paid POST can replay it or expose its Authorization.
        return None


class HttpTransport:
    """One network attempt per call; downloads always use a separate header set."""

    def __init__(self, config: Config):
        self.config = config
        self._opener = request.build_opener(_NoRedirect())

    def _read(self, response, limit: int, outcome: str) -> bytes:
        payload = response.read(limit + 1)
        if len(payload) > limit:
            raise MediaError("RESPONSE_TOO_LARGE", "Response exceeded the configured byte limit.", outcome)
        return payload

    def api(self, method: str, endpoint: str, body: bytes | None = None,
            content_type: str = "application/json") -> tuple[bytes, str]:
        if method not in {"GET", "POST"} or endpoint not in {
                "/models", "/images/generations", "/images/edits"}:
            raise MediaError("INVALID_OPERATION", "Unsupported API operation.")
        paid = method == "POST"
        outcome = "UNKNOWN" if paid else "READ_FAILED"
        headers = {"Authorization": "Bearer " + self.config.api_key,
                   "Accept": "application/json", "User-Agent": "enterprise-media/0.2.0"}
        if body is not None:
            headers["Content-Type"] = content_type
        req = request.Request(self.config.base_url + endpoint, data=body,
                              headers=headers, method=method)
        try:
            with self._opener.open(req, timeout=self.config.timeout) as response:
                return self._read(response, MAX_JSON_BYTES, outcome), response.headers.get("Content-Type", "")
        except error.HTTPError as exc:
            status = exc.code
            exc.close()
            if 300 <= status < 400:
                raise MediaError("API_REDIRECT_BLOCKED", "API redirect was blocked; verify the configured endpoint.",
                                 outcome, status) from None
            # An HTTP rejection does not imply that no fee was charged.
            rejected = 400 <= status < 500 and status not in {408, 409, 425}
            raise MediaError("API_HTTP_ERROR", "API returned an HTTP error; no retry was attempted.",
                             "REJECTED" if paid and rejected else outcome, status) from None
        except MediaError:
            raise
        except (error.URLError, socket.timeout, TimeoutError, OSError, ValueError, http.client.HTTPException):
            raise MediaError("API_TRANSPORT_ERROR", "API connection failed or timed out; no retry was attempted.",
                             outcome) from None

    def download(self, url: str) -> bytes:
        # Never attach API credentials, including to same-origin downloads.
        # Signed URLs remain in memory only and never enter an exception/receipt.
        for redirect_count in range(4):
            try:
                _validated_url(url, self.config.allow_loopback_http)
                req = request.Request(url, headers={"Accept": "image/*",
                                      "User-Agent": "enterprise-media/0.2.0"}, method="GET")
                with self._opener.open(req, timeout=self.config.timeout) as response:
                    return self._read(response, MAX_IMAGE_BYTES, "OUTPUT_UNAVAILABLE")
            except error.HTTPError as exc:
                status = exc.code
                location = exc.headers.get("Location")
                exc.close()
                if status in {301, 302, 303, 307, 308} and location and redirect_count < 3:
                    url = parse.urljoin(url, location)
                    continue
                raise MediaError("DOWNLOAD_HTTP_ERROR", "Image download failed; no generation retry was attempted.",
                                 "OUTPUT_UNAVAILABLE", status) from None
            except MediaError as exc:
                raise MediaError(exc.code, str(exc), "OUTPUT_UNAVAILABLE", exc.http_status) from None
            except (error.URLError, socket.timeout, TimeoutError, OSError, ValueError, http.client.HTTPException):
                raise MediaError("DOWNLOAD_FAILED", "Image download failed; no generation retry was attempted.",
                                 "OUTPUT_UNAVAILABLE") from None
        raise MediaError("DOWNLOAD_REDIRECT_LIMIT", "Image download redirect limit reached.", "OUTPUT_UNAVAILABLE")


def parse_json_response(payload: bytes, content_type: str, outcome: str) -> dict[str, Any]:
    media_type = content_type.split(";", 1)[0].strip().lower()
    if media_type != "application/json" and not media_type.endswith("+json"):
        raise MediaError("NON_JSON_RESPONSE", "API returned a non-JSON content type.", outcome)
    try:
        parsed = json.loads(payload.decode("utf-8-sig"))
    except (UnicodeError, ValueError, RecursionError):
        raise MediaError("INVALID_JSON", "API response could not be decoded as JSON.", outcome) from None
    if not isinstance(parsed, dict):
        raise MediaError("INVALID_RESPONSE", "API response must be a JSON object.", outcome)
    if parsed.get("error"):
        raise MediaError("PROVIDER_ERROR", "API reported an error; provider details were withheld.", outcome)
    return parsed


def _pillow():
    try:
        from PIL import Image
    except ImportError:
        raise MediaError("PILLOW_MISSING", "Install Pillow in this Python environment before generating images.") from None
    return Image


def inspect_image(payload: bytes) -> dict[str, Any]:
    Image = _pillow()
    if not payload or len(payload) > MAX_IMAGE_BYTES:
        raise MediaError("INVALID_IMAGE", "Image is empty or exceeds the byte limit.")
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(io.BytesIO(payload)) as img:
                image_format = img.format
                if image_format not in IMAGE_FORMATS:
                    raise ValueError()
                img.verify()
            with Image.open(io.BytesIO(payload)) as img:
                img.load()
                width, height = img.size
                if getattr(img, "n_frames", 1) != 1:
                    raise ValueError()
    except Exception:
        raise MediaError("INVALID_IMAGE", "Image failed static PNG/JPEG/WebP decoding or size checks.") from None
    extension, mime_type = IMAGE_FORMATS[image_format]
    return {"width": width, "height": height, "format": image_format,
            "extension": extension, "mime_type": mime_type, "bytes": len(payload),
            "sha256": hashlib.sha256(payload).hexdigest()}


def _read_local(path: Path, limit: int, label: str) -> bytes:
    try:
        with path.open("rb") as handle:
            value = handle.read(limit + 1)
        if len(value) > limit:
            raise OSError()
        return value
    except OSError:
        raise MediaError("INPUT_UNREADABLE", label + " is missing, unreadable or too large.") from None


def _multipart(fields: dict[str, Any], references: list[tuple[bytes, dict[str, Any]]]) -> tuple[bytes, str]:
    boundary = "media-" + uuid.uuid4().hex
    chunks: list[bytes] = []
    for key, value in fields.items():
        text_value = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, allow_nan=False)
        chunks.append((f'--{boundary}\r\nContent-Disposition: form-data; name="{key}"\r\n\r\n'
                       + text_value + "\r\n").encode("utf-8"))
    for index, (payload, details) in enumerate(references, 1):
        # Neutral filenames prevent leaking original personal file names.
        chunks.append((f'--{boundary}\r\nContent-Disposition: form-data; name="image[]"; '
                       f'filename="reference_{index}{details["extension"]}"\r\n'
                       f'Content-Type: {details["mime_type"]}\r\n\r\n').encode("ascii"))
        chunks.extend([payload, b"\r\n"])
    chunks.append(f"--{boundary}--\r\n".encode("ascii"))
    return b"".join(chunks), "multipart/form-data; boundary=" + boundary


def _parameters(model: str, prompt: str, size: str | None, quality: str | None,
                extra: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(model, str) or not model.strip() or len(model) > 200:
        raise MediaError("INVALID_MODEL", "A nonempty provider model identifier is required.")
    if not isinstance(prompt, str) or not prompt.strip():
        raise MediaError("EMPTY_PROMPT", "A nonempty prompt is required.")
    fields: dict[str, Any] = {"model": model, "prompt": prompt, "n": 1}
    if size is not None:
        fields["size"] = size
    if quality is not None:
        fields["quality"] = quality
    if extra is not None:
        if not isinstance(extra, dict):
            raise MediaError("INVALID_PARAMETERS", "Compatibility parameters must be a JSON object.")
        for key, value in extra.items():
            if not isinstance(key, str) or not re.fullmatch(r"[A-Za-z][A-Za-z0-9_]{0,63}", key):
                raise MediaError("INVALID_PARAMETERS", "Compatibility parameter names must be simple identifiers.")
            if key.lower() in PROTECTED_PARAMS or key in fields:
                raise MediaError("PROTECTED_PARAMETER", "Compatibility parameters cannot override credentials or explicit request fields.")
            fields[key] = value
    try:
        json.dumps(fields, allow_nan=False)
    except (ValueError, TypeError, RecursionError):
        raise MediaError("INVALID_PARAMETERS", "Compatibility parameters must contain finite JSON values.") from None
    return fields


def _public_request_value(value: Any, kind: str) -> str | int | None:
    """Expose ordinary selection values while keeping arbitrary provider fields private."""
    patterns = {"size": r"[0-9]{2,5}x[0-9]{2,5}|auto",
                "quality": r"[A-Za-z0-9_-]{1,32}", "seed": r"[0-9]{1,20}"}
    if isinstance(value, int) and not isinstance(value, bool) and kind == "seed" and 0 <= value < 2**64:
        return value
    if isinstance(value, str) and re.fullmatch(patterns[kind], value):
        return value
    return None


def _dpapi(payload: bytes, decrypt: bool) -> bytes:
    """Protect a recovery capsule for the current Windows user."""
    class Blob(ctypes.Structure):
        _fields_ = [("size", ctypes.c_ulong), ("data", ctypes.POINTER(ctypes.c_ubyte))]

    source = ctypes.create_string_buffer(payload)
    input_blob = Blob(len(payload), ctypes.cast(source, ctypes.POINTER(ctypes.c_ubyte)))
    output_blob = Blob()
    crypt = ctypes.windll.crypt32
    operation = crypt.CryptUnprotectData if decrypt else crypt.CryptProtectData
    operation.argtypes = ([ctypes.POINTER(Blob), ctypes.c_void_p, ctypes.c_void_p,
                           ctypes.c_void_p, ctypes.c_void_p, ctypes.c_ulong,
                           ctypes.POINTER(Blob)] if decrypt else
                          [ctypes.POINTER(Blob), ctypes.c_void_p, ctypes.c_void_p,
                           ctypes.c_void_p, ctypes.c_void_p, ctypes.c_ulong,
                           ctypes.POINTER(Blob)])
    operation.restype = ctypes.c_int
    if not operation(ctypes.byref(input_blob), None, None, None, None, 0,
                     ctypes.byref(output_blob)):
        raise MediaError("RECOVERY_PROTECTION_FAILED", "Private recovery data could not be protected or opened.",
                         "OUTPUT_UNAVAILABLE")
    try:
        return ctypes.string_at(output_blob.data, output_blob.size)
    finally:
        free = ctypes.windll.kernel32.LocalFree
        free.argtypes = [ctypes.c_void_p]
        free.restype = ctypes.c_void_p
        free(ctypes.cast(output_blob.data, ctypes.c_void_p))


class RecoveryCapsule:
    """Private durable copy of one returned result; never included in JSON receipts."""

    def __init__(self, output: Path, run_id: str):
        self.path = output.with_suffix(".recovery.bin")
        self.run_id = run_id

    def create(self, item: dict[str, Any], response: dict[str, Any],
               allow_loopback_http: bool) -> None:
        if isinstance(item.get("b64_json"), str) and item["b64_json"]:
            result = {"kind": "base64", "value": item["b64_json"]}
        elif isinstance(item.get("url"), str):
            result = {"kind": "url", "value": _validated_url(item["url"], allow_loopback_http)}
        else:
            raise MediaError("INVALID_DOWNLOAD_REFERENCE", "API returned an invalid image download reference.",
                             "OUTPUT_UNAVAILABLE")
        identifiers = {scope + "_" + key: value[key]
                       for scope, value in (("result", item), ("response", response))
                       for key in ("id", "task_id", "request_id")
                       if isinstance(value.get(key), str) and 0 < len(value[key]) <= 512
                       and all(32 <= ord(char) < 0xD800 or 0xE000 <= ord(char) <= 0x10FFFF
                               for char in value[key])}
        payload = json.dumps({"version": 1, "run_id": self.run_id, "result": result,
                              "provider_identifiers": identifiers}, ensure_ascii=True).encode("utf-8")
        if len(payload) > MAX_RECOVERY_BYTES:
            raise MediaError("RECOVERY_TOO_LARGE", "Returned result exceeded the recovery byte limit.",
                             "OUTPUT_UNAVAILABLE")
        protected = b"DPAPI1\n" + _dpapi(payload, False) if os.name == "nt" else b"PRIVATE1\n" + payload
        descriptor = None
        created = False
        try:
            descriptor = os.open(self.path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_BINARY", 0), 0o600)
            created = True
            with os.fdopen(descriptor, "wb") as handle:
                descriptor = None
                handle.write(protected)
                handle.flush()
                os.fsync(handle.fileno())
        except OSError:
            # A partial capsule cannot be used and must not mask a future attempt.
            if descriptor is not None:
                os.close(descriptor)
            if created:
                try:
                    self.path.unlink(missing_ok=True)
                except OSError:
                    pass
            raise MediaError("RECOVERY_SAVE_FAILED", "Private recovery data could not be saved.",
                             "OUTPUT_UNAVAILABLE") from None

    def read_payload(self) -> dict[str, Any]:
        try:
            if self.path.is_symlink():
                raise OSError()
            if os.name != "nt" and stat.S_IMODE(self.path.stat().st_mode) & 0o077:
                raise OSError()
            with self.path.open("rb") as handle:
                protected = handle.read(MAX_RECOVERY_BYTES + 1024 * 1024 + 1)
            if len(protected) > MAX_RECOVERY_BYTES + 1024 * 1024:
                raise OSError()
            if os.name == "nt" and protected.startswith(b"DPAPI1\n"):
                payload = _dpapi(protected[7:], True)
            elif os.name != "nt" and protected.startswith(b"PRIVATE1\n"):
                payload = protected[9:]
            else:
                raise OSError()
            value = json.loads(payload)
            if (not isinstance(value, dict) or value.get("version") != 1 or
                    value.get("run_id") != self.run_id or
                    not isinstance(value.get("result"), dict) or
                    value["result"].get("kind") not in {"base64", "url"} or
                    not isinstance(value["result"].get("value"), str)):
                raise ValueError()
            if (not isinstance(value.get("provider_identifiers"), dict) or
                    any(not isinstance(key, str) or not isinstance(identifier, str) or
                        len(identifier) > 512 for key, identifier in value["provider_identifiers"].items())):
                raise ValueError()
            return value
        except (OSError, ValueError, UnicodeError, RecursionError, TypeError):
            raise MediaError("RECOVERY_UNAVAILABLE", "Private recovery data is missing, unreadable or invalid.",
                             "OUTPUT_UNAVAILABLE") from None

    def read(self) -> dict[str, Any]:
        return self.read_payload()["result"]

    def remove(self) -> None:
        try:
            self.path.unlink(missing_ok=True)
        except OSError:
            pass  # The capsule remains private; a later recovery can clean it up.

    def staged_bytes(self, image: dict[str, Any] | None) -> bytes | None:
        """A full private .part from a crashed save can outlive an expiring URL."""
        if not isinstance(image, dict) or not isinstance(image.get("sha256"), str):
            return None
        for path in self.path.parent.glob(".media-" + self.run_id + "-*.part"):
            try:
                if path.is_symlink():
                    continue
                payload = _read_local(path, MAX_IMAGE_BYTES, "Staged image")
                if inspect_image(payload)["sha256"] == image["sha256"]:
                    return payload
            except MediaError:
                continue
        return None

    def remove_staged(self) -> None:
        for path in self.path.parent.glob(".media-" + self.run_id + "-*.part"):
            try:
                if not path.is_symlink():
                    path.unlink(missing_ok=True)
            except OSError:
                pass


class Receipt:
    """Exclusive initial creation; later updates replace only this run's receipt."""

    def __init__(self, output: Path, value: dict[str, Any]):
        self.output = output
        self.path = output.with_suffix(".receipt.json")
        self.value = value
        try:
            output.parent.mkdir(parents=True, exist_ok=True)
            candidates = {output, self.path, output.with_suffix(".recovery.bin")}
            candidates.update(output.with_suffix(suffix) for suffix in {".png", ".jpg", ".jpeg", ".webp"})
            if any(path.exists() or path.is_symlink() for path in candidates):
                raise MediaError("OUTPUT_EXISTS", "Output name or receipt already exists; no request was submitted.")
            with self.path.open("x", encoding="utf-8") as handle:
                json.dump(self.value, handle, ensure_ascii=False, indent=2)
                handle.flush()
                os.fsync(handle.fileno())
        except FileExistsError:
            raise MediaError("OUTPUT_EXISTS", "Output receipt already exists; no request was submitted.") from None
        except OSError:
            raise MediaError("OUTPUT_UNWRITABLE", "Output location is not writable; no request was submitted.") from None

    @classmethod
    def open_existing(cls, output: Path) -> "Receipt":
        path = output.with_suffix(".receipt.json")
        try:
            if path.is_symlink():
                raise OSError()
            with path.open("rb") as handle:
                payload = handle.read(1024 * 1024 + 1)
            if len(payload) > 1024 * 1024:
                raise ValueError()
            value = json.loads(payload)
            if (not isinstance(value, dict) or
                    not isinstance(value.get("run_id"), str) or
                    not re.fullmatch(r"[0-9a-f]{32}", value["run_id"]) or
                    value.get("operation") not in {"generate", "edit"} or
                    value.get("post_attempts") != 1):
                raise ValueError()
        except (OSError, ValueError, UnicodeError, RecursionError, TypeError):
            raise MediaError("INVALID_RECEIPT", "An existing paid-run receipt is required for recovery.",
                             "OUTPUT_UNAVAILABLE") from None
        receipt = cls.__new__(cls)
        receipt.output = output
        receipt.path = path
        receipt.value = value
        return receipt

    def update(self, **fields: Any) -> None:
        self.value.update(fields, updated_at=_utc_now())
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=self.path.parent,
                                             prefix=".media-receipt-", suffix=".tmp", delete=False) as handle:
                temporary = Path(handle.name)
                json.dump(self.value, handle, ensure_ascii=False, indent=2)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, self.path)
        except OSError:
            raise MediaError("RECEIPT_WRITE_FAILED", "Run receipt could not be updated; reconcile the existing receipt before another submission.",
                             self.value.get("submission_outcome", "UNKNOWN")) from None
        finally:
            if temporary is not None and temporary.exists():
                temporary.unlink(missing_ok=True)


class MediaClient:
    def __init__(self, config: Config, transport: HttpTransport | None = None):
        self.config = config
        self.transport = transport or HttpTransport(config)

    def models(self) -> dict[str, Any]:
        raw, content_type = self.transport.api("GET", "/models")
        data = parse_json_response(raw, content_type, "READ_FAILED")
        models = data.get("data")
        if not isinstance(models, list):
            raise MediaError("INVALID_MODEL_LIST", "Models response has no data array.", "READ_FAILED")
        # Ignore remote metadata, messages and URLs. Expose only provider model IDs.
        identifiers = sorted({item["id"] for item in models if isinstance(item, dict)
                              and isinstance(item.get("id"), str) and item["id"]
                              and "://" not in item["id"] and len(item["id"]) <= 200})
        return {"status": "READ_OK", "model_ids": identifiers,
                "note": "Provider identifiers; listing does not verify generation support or quality."}

    def generate(self, *, model: str, prompt: str, output: Path | str,
                 size: str | None = None, quality: str | None = None,
                 extra: dict[str, Any] | None = None) -> dict[str, Any]:
        return self._image("generate", model, prompt, output, [], size, quality, extra)

    def edit(self, *, model: str, prompt: str, output: Path | str,
             references: list[Path | str], size: str | None = None,
             quality: str | None = None, extra: dict[str, Any] | None = None) -> dict[str, Any]:
        return self._image("edit", model, prompt, output, references, size, quality, extra)

    def recover(self, output: Path | str) -> dict[str, Any]:
        """Finish a saved result without contacting the paid generation endpoint."""
        output = Path(output)
        if output.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp"} or not output.stem:
            raise MediaError("INVALID_OUTPUT", "Output name must have a PNG, JPEG or WebP extension.")
        receipt = Receipt.open_existing(output)
        capsule = RecoveryCapsule(output, receipt.value["run_id"])
        image = receipt.value.get("image")
        if isinstance(image, dict) and self._existing_output_matches(output, image):
            if receipt.value.get("status") != "TECHNICAL_SUCCESS":
                receipt.update(status="TECHNICAL_SUCCESS", submission_outcome="RESPONSE_RECEIVED",
                               recovery_available=False, receipt_file=receipt.path.name,
                               next_action="Review image content and actual dimensions against the approved brief.")
            capsule.remove()
            capsule.remove_staged()
            return receipt.value
        if not capsule.path.exists():
            raise MediaError("RECOVERY_UNAVAILABLE", "No saved result is available for this run; reconcile it with the provider.",
                             "OUTPUT_UNAVAILABLE")
        try:
            result = capsule.read()
            image_bytes = capsule.staged_bytes(image) or self._result_bytes(result)
            return self._save_result(receipt, capsule, image_bytes)
        except MediaError as exc:
            try:
                receipt.update(status="FAILED", submission_outcome="OUTPUT_UNAVAILABLE",
                               recovery_attempts=receipt.value.get("recovery_attempts", 0) + 1,
                               last_recovery_error=exc.safe_dict(),
                               next_action="Keep the private recovery file; retry recover after fixing the local or download error. Never re-submit this run.")
            except MediaError:
                exc.receipt_update_failed = True
            exc.outcome = "OUTPUT_UNAVAILABLE"
            raise

    def recovery_info(self, output: Path | str, show_provider_ids: bool = False) -> dict[str, Any]:
        """Describe the saved result; expose provider IDs only by explicit request."""
        output = Path(output)
        receipt = Receipt.open_existing(output)
        payload = RecoveryCapsule(output, receipt.value["run_id"]).read_payload()
        identifiers = payload["provider_identifiers"]
        result = {"status": "RECOVERY_AVAILABLE", "run_id": receipt.value["run_id"],
                  "result_kind": payload["result"]["kind"],
                  "provider_identifiers_available": bool(identifiers)}
        if show_provider_ids:
            result["provider_identifiers"] = identifiers
        return result

    def _result_bytes(self, result: dict[str, str]) -> bytes:
        if result["kind"] == "base64":
            try:
                return base64.b64decode(result["value"], validate=True)
            except (ValueError, TypeError, binascii.Error):
                raise MediaError("INVALID_BASE64", "API image bytes were not valid base64.",
                                 "OUTPUT_UNAVAILABLE") from None
        _validated_url(result["value"], self.config.allow_loopback_http)
        return self.transport.download(result["value"])

    @staticmethod
    def _existing_output_matches(output: Path, image: dict[str, Any]) -> bool:
        if not isinstance(image.get("file"), str) or not isinstance(image.get("sha256"), str):
            return False
        final = output.parent / image["file"]
        if final.name not in {output.with_suffix(ext).name for ext in (".png", ".jpg", ".webp")}:
            return False
        try:
            if final.is_symlink():
                return False
            payload = _read_local(final, MAX_IMAGE_BYTES, "Saved image")
            return hashlib.sha256(payload).hexdigest() == image["sha256"] and inspect_image(payload)["sha256"] == image["sha256"]
        except MediaError:
            return False

    def _save_result(self, receipt: Receipt, capsule: RecoveryCapsule,
                     image_bytes: bytes) -> dict[str, Any]:
        details = inspect_image(image_bytes)
        actual_output = receipt.output.with_suffix(details.pop("extension"))
        image = {"file": actual_output.name, **details}
        if actual_output.exists() or actual_output.is_symlink():
            if receipt.value.get("image") != image or not self._existing_output_matches(receipt.output, image):
                raise MediaError("OUTPUT_EXISTS_AFTER_SUBMIT", "Image output name appeared during generation; existing file was preserved.",
                                 "OUTPUT_UNAVAILABLE")
        else:
            receipt.update(status="OUTPUT_READY", submission_outcome="RESPONSE_RECEIVED", image=image)
            temporary = None
            try:
                with tempfile.NamedTemporaryFile(mode="wb", dir=actual_output.parent,
                                                 prefix=".media-" + receipt.value["run_id"] + "-",
                                                 suffix=".part", delete=False) as handle:
                    temporary = Path(handle.name)
                    handle.write(image_bytes)
                    handle.flush()
                    os.fsync(handle.fileno())
                # A same-directory hard link publishes the fully written image without replacing a concurrent file.
                os.link(temporary, actual_output)
            except FileExistsError:
                raise MediaError("OUTPUT_EXISTS_AFTER_SUBMIT", "Image output name appeared during generation; existing file was preserved.",
                                 "OUTPUT_UNAVAILABLE") from None
            except OSError:
                raise MediaError("OUTPUT_WRITE_FAILED", "Image could not be saved completely; recover this run after fixing the location.",
                                 "OUTPUT_UNAVAILABLE") from None
            finally:
                if temporary is not None:
                    try:
                        temporary.unlink(missing_ok=True)
                    except OSError:
                        pass
        receipt.update(status="TECHNICAL_SUCCESS", submission_outcome="RESPONSE_RECEIVED",
                       image=image, recovery_available=False, receipt_file=receipt.path.name,
                       next_action="Review image content and actual dimensions against the approved brief.")
        capsule.remove()
        capsule.remove_staged()
        return receipt.value

    def _image(self, operation, model, prompt, output, reference_paths, size, quality, extra):
        fields = _parameters(model, prompt, size, quality, extra)
        _pillow()  # Check dependency before any paid submission.
        if operation == "edit" and not 1 <= len(reference_paths) <= MAX_REFERENCES:
            raise MediaError("REFERENCES_REQUIRED", "Image editing requires between 1 and 16 reference files.")
        references = []
        for reference_path in reference_paths:
            payload = _read_local(Path(reference_path), MAX_IMAGE_BYTES, "A reference image")
            references.append((payload, inspect_image(payload)))
        endpoint = "/images/edits" if operation == "edit" else "/images/generations"
        if operation == "edit":
            body, content_type = _multipart(fields, references)
        else:
            body = json.dumps(fields, ensure_ascii=False, allow_nan=False).encode("utf-8")
            content_type = "application/json"
        output = Path(output)
        if output.suffix.lower() not in {".png", ".jpg", ".jpeg", ".webp"} or not output.stem:
            raise MediaError("INVALID_OUTPUT", "Output name must have a PNG, JPEG or WebP extension.")
        receipt = Receipt(output, {"schema_version": "0.2.0", "run_id": uuid.uuid4().hex,
            "created_at": _utc_now(), "operation": operation, "status": "PREPARED",
            "submission_outcome": "NOT_SUBMITTED", "post_attempts": 0,
            "model": model,
            "requested_size": _public_request_value(fields.get("size"), "size"),
            "requested_quality": _public_request_value(fields.get("quality"), "quality"),
            "requested_seed": _public_request_value(fields.get("seed"), "seed"),
            "request_fields_sha256": hashlib.sha256(json.dumps(fields, ensure_ascii=False, sort_keys=True,
                separators=(",", ":"), allow_nan=False).encode("utf-8")).hexdigest(),
            "requested_count": 1, "compatibility_parameter_names": sorted(extra or {}),
            "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
            "reference_images": [details for _, details in references],
            "billing_status": "NOT_VERIFIED", "content_quality": "NOT_REVIEWED"})
        capsule = RecoveryCapsule(output, receipt.value["run_id"])
        submitted = False
        response_received = False
        try:
            receipt.update(status="IN_FLIGHT", submission_outcome="UNKNOWN", post_attempts=1)
            submitted = True
            raw, returned_type = self.transport.api("POST", endpoint, body, content_type)
            response = parse_json_response(raw, returned_type, "UNKNOWN")
            data = response.get("data")
            if not isinstance(data, list) or len(data) != 1 or not isinstance(data[0], dict):
                raise MediaError("UNEXPECTED_IMAGE_RESPONSE", "API did not return exactly one image result.", "UNKNOWN")
            item = data[0]
            if not item.get("b64_json") and not item.get("url"):
                raise MediaError("IMAGE_RESULT_MISSING", "API image result contained neither bytes nor a download URL.", "UNKNOWN")
            response_received = True
            capsule.create(item, response, self.config.allow_loopback_http)
            receipt.update(status="RESPONSE_RECEIVED", submission_outcome="RESPONSE_RECEIVED",
                           recovery_available=True)
            return self._save_result(receipt, capsule,
                                     self._result_bytes(capsule.read()))
        except MediaError as exc:
            outcome = "NOT_SUBMITTED" if not submitted else ("OUTPUT_UNAVAILABLE" if response_received else exc.outcome)
            if submitted and outcome == "NOT_SUBMITTED":
                outcome = "UNKNOWN"
            try:
                receipt.update(status="FAILED", submission_outcome=outcome,
                    post_attempts=1 if submitted else 0,
                    error={**exc.safe_dict(), "outcome": outcome},
                    recovery_available=capsule.path.exists(),
                    next_action=("Run recover with the original --output after fixing the download or disk issue; do not re-submit."
                                 if capsule.path.exists() else
                                 "Check this run with the provider before considering a new paid attempt; no automatic retry occurred."))
            except MediaError:
                # Surface the failed audit write while preserving the original error.
                exc.receipt_update_failed = True
            exc.outcome = outcome
            raise


class _SafeArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        # argparse normally echoes invalid argv, which might contain a secret.
        raise MediaError("INVALID_ARGUMENTS", "Invalid command arguments; use --help for accepted options.")


def main(argv: list[str] | None = None) -> int:
    parser = _SafeArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--timeout", type=float, default=300.0, help="One network attempt timeout in seconds.")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("models", help="Read-only model list; does not prove generation support.")
    recovery_parser = commands.add_parser("recover", help="Finish a saved result without another paid POST.")
    recovery_parser.add_argument("--output", type=Path, required=True,
                                 help="Original requested output path, not the receipt or recovery file.")
    info_parser = commands.add_parser("recovery-info", help="Inspect a saved result without revealing its signed URL.")
    info_parser.add_argument("--output", type=Path, required=True)
    info_parser.add_argument("--show-provider-ids", action="store_true",
                             help="Explicitly print private provider identifiers for authorized reconciliation.")
    for operation in ("generate", "edit"):
        subparser = commands.add_parser(operation)
        subparser.add_argument("--model", required=True)
        subparser.add_argument("--prompt-file", type=Path, required=True)
        subparser.add_argument("--output", type=Path, required=True)
        subparser.add_argument("--size")
        subparser.add_argument("--quality")
        subparser.add_argument("--params-file", type=Path, help="Provider compatibility parameters as a JSON object.")
        if operation == "edit":
            subparser.add_argument("--reference", type=Path, action="append", required=True)
    try:
        args = parser.parse_args(argv)
        config = (Config.for_recovery(timeout=args.timeout) if args.command in {"recover", "recovery-info"}
                  else Config.from_env(timeout=args.timeout))
        client = MediaClient(config)
        if args.command == "models":
            result = client.models()
        elif args.command == "recover":
            result = client.recover(args.output)
        elif args.command == "recovery-info":
            result = client.recovery_info(args.output, args.show_provider_ids)
        else:
            try:
                prompt = _read_local(args.prompt_file, 1024 * 1024, "Prompt file").decode("utf-8-sig")
                extra = json.loads(_read_local(args.params_file, 1024 * 1024, "Parameter file").decode("utf-8-sig")) if args.params_file else None
            except (UnicodeError, ValueError, RecursionError):
                raise MediaError("INVALID_INPUT_TEXT", "Prompt must be UTF-8 and parameters must be valid JSON.") from None
            options = {"model": args.model, "prompt": prompt, "output": args.output,
                       "size": args.size, "quality": args.quality, "extra": extra}
            if args.command == "edit":
                result = client.edit(references=args.reference, **options)
            else:
                result = client.generate(**options)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except MediaError as exc:
        print(json.dumps({"status": "FAILED", **exc.safe_dict()}, ensure_ascii=False, indent=2))
        return 3 if exc.outcome in {"UNKNOWN", "OUTPUT_UNAVAILABLE"} else 2
    except (KeyboardInterrupt, Exception):
        # Do not print exception strings or traceback: they may embed signed URLs.
        print(json.dumps({"status": "FAILED", "code": "INTERRUPTED_OR_UNEXPECTED_ERROR",
                          "outcome": "UNKNOWN", "message": "Execution did not complete. Inspect the existing receipt before another submission."}))
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
