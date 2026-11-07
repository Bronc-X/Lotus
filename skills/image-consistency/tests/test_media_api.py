"""Offline behavioral tests. Only loopback test servers are contacted.

Run with a Python environment containing Pillow:
  python -m unittest discover -s tests -p test_media_api.py -v
"""

from __future__ import annotations

from contextlib import contextmanager, redirect_stdout
import base64
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import importlib.util
import io
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from unittest.mock import patch

from PIL import Image


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "media_api.py"
SPEC = importlib.util.spec_from_file_location("enterprise_media_api", MODULE_PATH)
media = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = media
SPEC.loader.exec_module(media)

FAKE_KEY = "unit-test-credential-only"


def image_bytes(width=11, height=17, image_format="PNG"):
    stream = io.BytesIO()
    Image.new("RGB", (width, height), "#8cb7a6").save(stream, format=image_format)
    return stream.getvalue()


def image_response(payload=None):
    return json.dumps({"data": [{"b64_json": base64.b64encode(payload or image_bytes()).decode("ascii")}]}).encode()


class FakeTransport:
    def __init__(self, payload=None, content_type="application/json"):
        self.payload = image_response() if payload is None else payload
        self.content_type = content_type
        self.calls = []

    def api(self, method, endpoint, body=None, content_type="application/json"):
        self.calls.append((method, endpoint, body, content_type))
        return self.payload, self.content_type

    def download(self, url):
        raise AssertionError("Unexpected download in this test.")


@contextmanager
def local_server(routes):
    calls = []

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def handle_request(self):
            body = self.rfile.read(int(self.headers.get("Content-Length", "0")))
            call = {"method": self.command, "path": self.path, "headers": dict(self.headers), "body": body}
            calls.append(call)
            status, headers, payload, delay = routes(call)
            if delay:
                time.sleep(delay)
            try:
                self.send_response(status)
                for key, value in headers.items():
                    self.send_header(key, value)
                self.end_headers()
                self.wfile.write(payload)
            except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError, socket.timeout):
                pass

        do_GET = handle_request
        do_POST = handle_request

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    server.daemon_threads = True
    thread = threading.Thread(target=server.serve_forever, kwargs={"poll_interval": 0.02}, daemon=True)
    thread.start()
    try:
        yield "http://127.0.0.1:" + str(server.server_port), calls
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=1)


def local_config(base, timeout=2):
    return media.Config.from_env({"MEDIA_API_BASE_URL": base + "/v1", "MEDIA_API_KEY": FAKE_KEY,
                                  "MEDIA_API_ALLOW_LOOPBACK_HTTP": "1"}, timeout=timeout)


class MediaApiTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.output = self.root / "result.png"
        self.config = media.Config.from_env({"MEDIA_API_BASE_URL": "https://unit-test.invalid/v1",
                                            "MEDIA_API_KEY": FAKE_KEY})

    def generate(self, transport, **kwargs):
        return media.MediaClient(self.config, transport).generate(model="provider-image-model", prompt="A small product card.",
                                                                 output=self.output, **kwargs)

    def receipt(self):
        return json.loads(self.output.with_suffix(".receipt.json").read_text(encoding="utf-8"))

    def test_actual_dimensions_hash_and_compatibility_parameters(self):
        payload = image_bytes(19, 23)
        transport = FakeTransport(image_response(payload))
        result = self.generate(transport, size="1024x1536", quality="high", extra={"response_format": "b64_json"})
        self.assertEqual(result["status"], "TECHNICAL_SUCCESS")
        self.assertEqual((result["image"]["width"], result["image"]["height"]), (19, 23))
        self.assertEqual(result["image"]["sha256"], hashlib.sha256(payload).hexdigest())
        self.assertEqual(self.output.read_bytes(), payload)
        self.assertEqual(json.loads(transport.calls[0][2])["response_format"], "b64_json")
        self.assertEqual(result["content_quality"], "NOT_REVIEWED")
        self.assertEqual(result["billing_status"], "NOT_VERIFIED")

    def test_receipt_tracks_effective_compatibility_fields_without_private_values(self):
        private_value = "https://private.unit-test.invalid/?signature=do-not-log"
        transport = FakeTransport()
        self.generate(transport, extra={"size": "1024x1536", "quality": "high",
                                        "seed": 1742, "provider_note": private_value})
        fields = json.loads(transport.calls[0][2])
        receipt = self.receipt()
        canonical = json.dumps(fields, ensure_ascii=False, sort_keys=True,
                               separators=(",", ":"), allow_nan=False).encode("utf-8")
        self.assertEqual(receipt["request_fields_sha256"], hashlib.sha256(canonical).hexdigest())
        self.assertEqual((receipt["requested_size"], receipt["requested_quality"], receipt["requested_seed"]),
                         ("1024x1536", "high", 1742))
        self.assertNotIn(private_value, json.dumps(receipt))

    def test_jpeg_response_uses_actual_extension(self):
        result = self.generate(FakeTransport(image_response(image_bytes(image_format="JPEG"))))
        self.assertEqual(result["image"]["file"], "result.jpg")
        self.assertFalse(self.output.exists())
        self.assertTrue(self.output.with_suffix(".jpg").is_file())

    def test_html_falsely_labelled_json_is_unknown_and_not_logged(self):
        private_text = "https://private.unit-test.invalid/?signature=do-not-log " + FAKE_KEY
        transport = FakeTransport(("<html>" + private_text + "</html>").encode())
        with self.assertRaises(media.MediaError) as error:
            self.generate(transport)
        self.assertEqual(error.exception.code, "INVALID_JSON")
        self.assertEqual(error.exception.outcome, "UNKNOWN")
        self.assertEqual(len(transport.calls), 1)
        logged = self.output.with_suffix(".receipt.json").read_text(encoding="utf-8")
        self.assertNotIn("private.unit-test.invalid", logged)
        self.assertNotIn("signature", logged)
        self.assertNotIn(FAKE_KEY, logged)
        self.assertEqual(self.receipt()["submission_outcome"], "UNKNOWN")

    def test_json_with_html_content_type_is_rejected(self):
        with self.assertRaises(media.MediaError) as error:
            self.generate(FakeTransport(content_type="text/html"))
        self.assertEqual(error.exception.code, "NON_JSON_RESPONSE")

    def test_missing_second_reference_prevents_any_submission(self):
        first = self.root / "person.png"
        first.write_bytes(image_bytes())
        transport = FakeTransport()
        with self.assertRaises(media.MediaError):
            media.MediaClient(self.config, transport).edit(model="provider-model", prompt="Use both references.",
                output=self.output, references=[first, self.root / "missing.png"])
        self.assertEqual(transport.calls, [])
        self.assertFalse(self.output.with_suffix(".receipt.json").exists())

    def test_empty_or_corrupt_references_prevent_submission(self):
        corrupt = self.root / "corrupt.png"
        corrupt.write_bytes(b"not an image")
        for references in ([], [corrupt]):
            with self.subTest(references=references):
                transport = FakeTransport()
                with self.assertRaises(media.MediaError):
                    media.MediaClient(self.config, transport).edit(model="provider-model", prompt="Use reference.",
                                                                  output=self.output, references=references)
                self.assertEqual(transport.calls, [])

    def test_multipart_sends_all_references_with_neutral_names(self):
        references = []
        for index in range(2):
            path = self.root / ("private-person-name-" + str(index) + ".png")
            path.write_bytes(image_bytes(width=11 + index))
            references.append(path)
        transport = FakeTransport()
        media.MediaClient(self.config, transport).edit(model="provider-model", prompt="Keep person and product.",
                output=self.output, references=references, extra={"response_format": "b64_json"})
        method, endpoint, body, content_type = transport.calls[0]
        self.assertEqual((method, endpoint), ("POST", "/images/edits"))
        self.assertEqual(body.count(b'name="image[]"'), 2)
        self.assertNotIn(b"private-person-name", body)
        self.assertIn(b'name="response_format"', body)
        self.assertIn("multipart/form-data; boundary=", content_type)
        self.assertEqual(len(self.receipt()["reference_images"]), 2)

    def test_timeout_is_one_paid_attempt_and_preserves_unknown_receipt(self):
        def slow_response(call):
            return 200, {"Content-Type": "application/json"}, image_response(), 0.2
        with local_server(slow_response) as (base, calls):
            client = media.MediaClient(local_config(base, timeout=0.04))
            with self.assertRaises(media.MediaError) as error:
                client.generate(model="test-model", prompt="Test.", output=self.output)
            self.assertEqual(error.exception.outcome, "UNKNOWN")
            self.assertEqual(len(calls), 1)
            self.assertEqual(calls[0]["headers"]["Authorization"], "Bearer " + FAKE_KEY)
            with self.assertRaises(media.MediaError) as duplicate:
                client.generate(model="test-model", prompt="Test.", output=self.output)
            self.assertEqual(duplicate.exception.code, "OUTPUT_EXISTS")
            self.assertEqual(len(calls), 1)
        self.assertEqual(self.receipt()["post_attempts"], 1)
        self.assertEqual(self.receipt()["submission_outcome"], "UNKNOWN")

    def test_download_and_cross_origin_redirect_never_receive_authorization(self):
        def image_route(call):
            return 200, {"Content-Type": "image/png"}, image_bytes(), 0
        with local_server(image_route) as (download_base, download_calls):
            def api_route(call):
                if call["method"] == "POST":
                    return 200, {"Content-Type": "application/json"}, json.dumps({"data": [{"url": api_base + "/signed-start?token=private-token"}]}).encode(), 0
                return 302, {"Location": download_base + "/image?signature=private-signature"}, b"", 0
            with local_server(api_route) as (api_base, api_calls):
                media.MediaClient(local_config(api_base)).generate(model="test-model", prompt="Test.", output=self.output)
        self.assertIn("Authorization", api_calls[0]["headers"])
        self.assertNotIn("Authorization", api_calls[1]["headers"])
        self.assertNotIn("Authorization", download_calls[0]["headers"])
        logged = self.output.with_suffix(".receipt.json").read_text(encoding="utf-8")
        for forbidden in (FAKE_KEY, api_base, download_base, "private-token", "private-signature"):
            self.assertNotIn(forbidden, logged)

    def test_failed_download_recovers_saved_url_without_second_post(self):
        signed_url = "https://signed.unit-test.invalid/image?token=private-result-token"
        provider_id = "private-provider-task-id"
        payload = json.dumps({"request_id": "private-response-request-id",
                              "data": [{"url": signed_url, "id": provider_id}]}).encode()
        class FlakyDownload(FakeTransport):
            def __init__(self):
                super().__init__(payload)
                self.downloads = 0

            def download(self, url):
                self.downloads += 1
                self_test.assertEqual(url, signed_url)
                if self.downloads == 1:
                    raise media.MediaError("DOWNLOAD_FAILED", "Image download failed.", "OUTPUT_UNAVAILABLE")
                return image_bytes()

        self_test = self
        transport = FlakyDownload()
        client = media.MediaClient(self.config, transport)
        with self.assertRaises(media.MediaError) as failure:
            client.generate(model="provider-image-model", prompt="Test.", output=self.output)
        self.assertEqual(failure.exception.outcome, "OUTPUT_UNAVAILABLE")
        self.assertEqual(self.receipt()["recovery_available"], True)
        self.assertEqual(len(transport.calls), 1)
        capsule = self.output.with_suffix(".recovery.bin")
        self.assertTrue(capsule.is_file())
        public_receipt = self.output.with_suffix(".receipt.json").read_text(encoding="utf-8")
        self.assertNotIn(signed_url, public_receipt)
        self.assertNotIn(provider_id, public_receipt)
        self.assertNotIn("private-response-request-id", public_receipt)
        safe_info = client.recovery_info(self.output)
        self.assertEqual(safe_info["result_kind"], "url")
        self.assertNotIn("provider_identifiers", safe_info)
        private_info = client.recovery_info(self.output, show_provider_ids=True)
        self.assertEqual(private_info["provider_identifiers"]["result_id"], provider_id)
        self.assertEqual(private_info["provider_identifiers"]["response_request_id"],
                         "private-response-request-id")
        if os.name == "nt":
            self.assertNotIn(signed_url.encode(), capsule.read_bytes())
            self.assertNotIn(provider_id.encode(), capsule.read_bytes())
        else:
            self.assertEqual(capsule.stat().st_mode & 0o077, 0)
        result = client.recover(self.output)
        self.assertEqual(result["status"], "TECHNICAL_SUCCESS")
        self.assertEqual(self.output.read_bytes(), image_bytes())
        self.assertEqual(len(transport.calls), 1)
        self.assertEqual(transport.downloads, 2)
        self.assertFalse(capsule.exists())

    def test_recover_does_not_overwrite_a_file_created_after_download_failure(self):
        class BrokenDownload(FakeTransport):
            def __init__(self):
                super().__init__(json.dumps({"data": [{"url": "https://signed.unit-test.invalid/image"}]}).encode())

            def download(self, url):
                if self_test.output.exists():
                    return image_bytes()
                raise media.MediaError("DOWNLOAD_FAILED", "Image download failed.", "OUTPUT_UNAVAILABLE")

        self_test = self
        transport = BrokenDownload()
        client = media.MediaClient(self.config, transport)
        with self.assertRaises(media.MediaError):
            client.generate(model="provider-image-model", prompt="Test.", output=self.output)
        self.output.write_bytes(b"someone else's valuable file")
        with self.assertRaises(media.MediaError) as failure:
            client.recover(self.output)
        self.assertEqual(failure.exception.code, "OUTPUT_EXISTS_AFTER_SUBMIT")
        self.assertEqual(self.output.read_bytes(), b"someone else's valuable file")
        self.assertEqual(len(transport.calls), 1)

    def test_process_death_after_staging_base64_result_is_recoverable_offline(self):
        program = f'''
import importlib.util, os, sys
from pathlib import Path
spec = importlib.util.spec_from_file_location("crash_media", {str(MODULE_PATH)!r})
media = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = media
spec.loader.exec_module(media)
class Transport:
    def api(self, *args):
        return {image_response()!r}, "application/json"
    def download(self, url):
        raise AssertionError("Unexpected download")
media.os.link = lambda *args: os._exit(55)
media.MediaClient(media.Config("https://unit-test.invalid/v1", "test"), Transport()).generate(
    model="test-model", prompt="Test.", output=Path({str(self.output)!r}))
'''
        completed = subprocess.run([sys.executable, "-c", program], capture_output=True, timeout=10)
        self.assertEqual(completed.returncode, 55, completed.stderr.decode(errors="replace"))
        self.assertEqual(self.receipt()["status"], "OUTPUT_READY")
        self.assertTrue(self.output.with_suffix(".recovery.bin").exists())
        self.assertFalse(self.output.exists())
        self.assertTrue(list(self.root.glob(".media-*.part")))
        transport = FakeTransport(b"should never be used")
        result = media.MediaClient(media.Config.for_recovery({}), transport).recover(self.output)
        self.assertEqual(result["status"], "TECHNICAL_SUCCESS")
        self.assertEqual(self.output.read_bytes(), image_bytes())
        self.assertEqual(transport.calls, [])
        self.assertEqual(list(self.root.glob(".media-*.part")), [])
        self.assertFalse(self.output.with_suffix(".recovery.bin").exists())

    def test_crash_after_final_file_before_success_receipt_recovers_without_rewrite(self):
        original_update = media.Receipt.update
        def crash_on_success(receipt, **fields):
            if fields.get("status") == "TECHNICAL_SUCCESS":
                raise KeyboardInterrupt()
            return original_update(receipt, **fields)

        transport = FakeTransport()
        with patch.object(media.Receipt, "update", crash_on_success):
            with self.assertRaises(KeyboardInterrupt):
                self.generate(transport)
        self.assertEqual(self.receipt()["status"], "OUTPUT_READY")
        original_stat = self.output.stat()
        with patch.object(media.os, "link", side_effect=AssertionError("Output must not be rewritten")):
            result = media.MediaClient(self.config, transport).recover(self.output)
        self.assertEqual(result["status"], "TECHNICAL_SUCCESS")
        self.assertEqual(self.output.stat().st_mtime_ns, original_stat.st_mtime_ns)
        self.assertEqual(len(transport.calls), 1)

    def test_cli_recover_base64_needs_no_provider_credentials(self):
        with patch.object(media.os, "link", side_effect=KeyboardInterrupt):
            with self.assertRaises(KeyboardInterrupt):
                self.generate(FakeTransport())
        stream = io.StringIO()
        # Preserve Windows profile variables needed by DPAPI while removing only API credentials.
        with patch.dict(os.environ) as environment, redirect_stdout(stream):
            environment.pop("MEDIA_API_BASE_URL", None)
            environment.pop("MEDIA_API_KEY", None)
            code = media.main(["recover", "--output", str(self.output)])
        self.assertEqual(code, 0, stream.getvalue())
        self.assertEqual(json.loads(stream.getvalue())["status"], "TECHNICAL_SUCCESS")

    def test_cli_recovers_signed_url_in_new_process_without_api_key(self):
        gets = 0
        def route(call):
            nonlocal gets
            if call["method"] == "POST":
                body = json.dumps({"data": [{"url": base + "/signed-image?token=private"}]}).encode()
                return 200, {"Content-Type": "application/json"}, body, 0
            gets += 1
            if gets == 1:
                return 503, {"Content-Type": "text/plain"}, b"temporary failure", 0
            return 200, {"Content-Type": "image/png"}, image_bytes(), 0

        with local_server(route) as (base, calls):
            with self.assertRaises(media.MediaError):
                media.MediaClient(local_config(base)).generate(model="test-model", prompt="Test.", output=self.output)
            environment = dict(os.environ)
            environment.pop("MEDIA_API_BASE_URL", None)
            environment.pop("MEDIA_API_KEY", None)
            environment["MEDIA_API_ALLOW_LOOPBACK_HTTP"] = "1"
            completed = subprocess.run([sys.executable, str(MODULE_PATH), "recover", "--output", str(self.output)],
                                       env=environment, capture_output=True, timeout=10)
        self.assertEqual(completed.returncode, 0, completed.stdout.decode(errors="replace"))
        self.assertEqual(self.output.read_bytes(), image_bytes())
        self.assertEqual([call["method"] for call in calls], ["POST", "GET", "GET"])
        self.assertNotIn("Authorization", calls[1]["headers"])
        self.assertNotIn("Authorization", calls[2]["headers"])

    def test_paid_post_redirect_is_not_followed_or_replayed(self):
        with local_server(lambda call: (200, {"Content-Type": "application/json"}, image_response(), 0)) as (target, target_calls):
            with local_server(lambda call: (307, {"Location": target + "/capture"}, b"", 0)) as (base, calls):
                with self.assertRaises(media.MediaError) as error:
                    media.MediaClient(local_config(base)).generate(model="test-model", prompt="Test.", output=self.output)
        self.assertEqual(error.exception.code, "API_REDIRECT_BLOCKED")
        self.assertEqual(error.exception.outcome, "UNKNOWN")
        self.assertEqual(len(calls), 1)
        self.assertEqual(target_calls, [])

    def test_same_output_and_alternate_extension_never_overwrite(self):
        for suffix in (".png", ".jpg", ".receipt.json"):
            with self.subTest(suffix=suffix):
                existing = self.output.with_suffix(suffix)
                existing.write_bytes(b"original valuable bytes")
                transport = FakeTransport()
                with self.assertRaises(media.MediaError) as error:
                    self.generate(transport)
                self.assertEqual(error.exception.code, "OUTPUT_EXISTS")
                self.assertEqual(existing.read_bytes(), b"original valuable bytes")
                self.assertEqual(transport.calls, [])
                existing.unlink()

    def test_file_created_during_request_is_not_overwritten(self):
        output = self.output
        class ConcurrentWriter(FakeTransport):
            def api(self, *args, **kwargs):
                output.write_bytes(b"someone else's image")
                return super().api(*args, **kwargs)
        with self.assertRaises(media.MediaError) as error:
            self.generate(ConcurrentWriter())
        self.assertEqual(error.exception.outcome, "OUTPUT_UNAVAILABLE")
        self.assertEqual(self.output.read_bytes(), b"someone else's image")

    def test_invalid_generated_bytes_record_output_failure(self):
        with self.assertRaises(media.MediaError) as error:
            self.generate(FakeTransport(image_response(b"not an image")))
        self.assertEqual(error.exception.outcome, "OUTPUT_UNAVAILABLE")
        self.assertEqual(self.receipt()["submission_outcome"], "OUTPUT_UNAVAILABLE")
        self.assertFalse(self.output.exists())

    def test_receipt_update_failure_is_reported_and_prevents_submission(self):
        transport = FakeTransport()
        failure = media.MediaError("RECEIPT_WRITE_FAILED", "Receipt update failed.", "UNKNOWN")
        with patch.object(media.Receipt, "update", side_effect=failure):
            with self.assertRaises(media.MediaError) as error:
                self.generate(transport)
        self.assertEqual(error.exception.outcome, "NOT_SUBMITTED")
        self.assertTrue(error.exception.safe_dict()["receipt_update_failed"])
        self.assertEqual(transport.calls, [])
        self.assertEqual(self.receipt()["post_attempts"], 0)

    def test_http_rejection_is_not_retried_and_does_not_claim_no_charge(self):
        with local_server(lambda call: (429, {"Content-Type": "text/html"},
                          b"private provider error details", 0)) as (base, calls):
            with self.assertRaises(media.MediaError) as error:
                media.MediaClient(local_config(base)).generate(model="test-model", prompt="Test.", output=self.output)
        self.assertEqual(error.exception.outcome, "REJECTED")
        self.assertEqual(len(calls), 1)
        self.assertEqual(self.receipt()["billing_status"], "NOT_VERIFIED")
        self.assertNotIn("private provider", json.dumps(self.receipt()))

    def test_models_is_read_only_and_drops_other_metadata(self):
        transport = FakeTransport(json.dumps({"data": [{"id": "provider/model-2.5", "url": "https://private.invalid"},
                                                       {"id": "https://private.invalid/key"}]}).encode())
        result = media.MediaClient(self.config, transport).models()
        self.assertEqual(result["model_ids"], ["provider/model-2.5"])
        self.assertEqual(transport.calls[0][0:2], ("GET", "/models"))
        self.assertEqual(list(self.root.iterdir()), [])

    def test_protected_or_invalid_parameters_prevent_submission(self):
        for extra in ({"api_key": "do-not-send"}, {"n": 4}, {"bad\r\nheader": "x"}, {"value": float("nan")}):
            with self.subTest(extra=extra):
                transport = FakeTransport()
                with self.assertRaises(media.MediaError):
                    self.generate(transport, extra=extra)
                self.assertEqual(transport.calls, [])

    def test_config_rejects_unsafe_urls_without_echoing_values(self):
        for base in ("https://name:private-password@unit-test.invalid/v1", "http://unit-test.invalid/v1",
                     "https://unit-test.invalid/v1?key=private-key", "https://unit-test.invalid:invalid/v1"):
            with self.subTest(base=base), self.assertRaises(media.MediaError) as error:
                media.Config.from_env({"MEDIA_API_BASE_URL": base, "MEDIA_API_KEY": FAKE_KEY})
            self.assertNotIn("unit-test.invalid", str(error.exception))
            self.assertNotIn("private", str(error.exception))
        self.assertNotIn(FAKE_KEY, repr(self.config))

    def test_cli_does_not_echo_unknown_secret_arguments(self):
        stream = io.StringIO()
        with redirect_stdout(stream):
            code = media.main(["models", "--api-key", "private-command-line-secret"])
        self.assertEqual(code, 2)
        self.assertNotIn("private-command-line-secret", stream.getvalue())


if __name__ == "__main__":
    unittest.main()
