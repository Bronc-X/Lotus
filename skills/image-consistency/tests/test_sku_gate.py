"""Offline contract and release tests; no provider requests."""

import base64
from contextlib import redirect_stdout
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import threading
import types
import unittest
from unittest.mock import patch

from PIL import Image


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "sku_gate.py"
SPEC = importlib.util.spec_from_file_location("sku_gate", MODULE_PATH)
gate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(gate)


def png_bytes(color: str) -> bytes:
    stream = io.BytesIO()
    Image.new("RGB", (16, 18), color).save(stream, format="PNG")
    return stream.getvalue()


class SkuGateTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.refs = self.root / "refs"
        self.refs.mkdir()
        self.identity = self.refs / "identity.png"
        self.product = self.refs / "product.png"
        self.identity.write_bytes(png_bytes("#957664"))
        self.product.write_bytes(png_bytes("#d31c39"))
        self.contract_path = self.refs / "sku.json"
        self.contract = {
            "schema_version": "1.0", "sku_id": "sku-1", "version": "v1",
            "approval": {"status": "APPROVED", "reviewer": "Product owner", "approved_at": "2026-09-29"},
            "references": {"identity": {"path": "identity.png", "sha256": gate.digest(self.identity)},
                           "product": {"path": "product.png", "sha256": gate.digest(self.product)}},
            "must_preserve": [{"id": "red-vest", "description": "Red vest with wide ribbed hem",
                               "source_evidence": "Product front photo"}],
            "unknown_or_unverified": ["Back construction not photographed"],
            "creative_brief": "Full body on white background"}
        self.save_contract()
        self.job_dir = self.root / "job"

    def save_contract(self):
        self.contract_path.write_text(json.dumps(self.contract), encoding="utf-8")

    def prepare(self):
        return gate.prepare(types.SimpleNamespace(spec=str(self.contract_path), job_dir=str(self.job_dir),
                                                  model="example-model", size="1024x1536", quality="high"))

    def candidate(self):
        plan = self.prepare()
        path = self.job_dir / "candidate.png"
        path.write_bytes(png_bytes("#cc1531"))
        receipt = {"status": "TECHNICAL_SUCCESS", "run_id": "run-1", "model": plan["model"],
                   "prompt_sha256": plan["prompt_sha256"], "requested_size": plan["size"],
                   "requested_quality": plan["quality"],
                   "reference_images": [{"sha256": plan["reference_sha256"]["identity"]},
                                        {"sha256": plan["reference_sha256"]["product"]}],
                   "image": {"file": path.name, "sha256": gate.digest(path)}}
        (self.job_dir / "candidate.receipt.json").write_text(json.dumps(receipt), encoding="utf-8")
        return path

    def review(self, path: Path, status="PASS") -> Path:
        review = {"reviewer": "Product owner", "candidate_sha256": gate.digest(path),
                  "unknowns_not_claimed": True,
                  "checks": {"red-vest": {"status": status, "evidence_note": "Compared hem with front product photo"}}}
        review_path = self.job_dir / "quality-review.json"
        review_path.write_text(json.dumps(review), encoding="utf-8")
        return review_path

    def test_unapproved_source_facts_block_job_before_submission(self):
        self.contract["approval"] = {"status": "DRAFT", "reviewer": None, "approved_at": None}
        self.save_contract()
        with self.assertRaisesRegex(gate.GateError, "approval"):
            self.prepare()
        self.assertFalse(self.job_dir.exists())

    def test_changed_product_blocks_generation(self):
        self.prepare()
        self.product.write_bytes(png_bytes("#127bb1"))
        with patch.object(gate.subprocess, "run") as runner:
            with self.assertRaisesRegex(gate.GateError, "Changed product"):
                gate.generate(types.SimpleNamespace(job_dir=str(self.job_dir)))
            runner.assert_not_called()

    def test_failed_feature_cannot_publish(self):
        candidate = self.candidate()
        review = self.review(candidate, "FAIL")
        with self.assertRaisesRegex(gate.GateError, "Feature not approved"):
            gate.release(types.SimpleNamespace(job_dir=str(self.job_dir), review=str(review)))
        self.assertFalse((self.job_dir / "approved" / "release.json").exists())

    def test_approval_binds_source_candidate_and_review(self):
        candidate = self.candidate()
        review = self.review(candidate)
        gate.release(types.SimpleNamespace(job_dir=str(self.job_dir), review=str(review)))
        result = gate.verify(types.SimpleNamespace(job_dir=str(self.job_dir)))
        self.assertEqual(result["sha256"], gate.digest(candidate))
        self.assertTrue(Path(result["approved_file"]).is_file())
        review.write_text(review.read_text(encoding="utf-8") + " ", encoding="utf-8")
        with self.assertRaisesRegex(gate.GateError, "Approval review changed"):
            gate.verify(types.SimpleNamespace(job_dir=str(self.job_dir)))

    def test_release_can_finish_after_copy_was_published_before_manifest(self):
        candidate = self.candidate()
        review = self.review(candidate)
        approved_dir = self.job_dir / "approved"
        approved_dir.mkdir()
        orphan = approved_dir / "sku-1-v1.png"
        orphan.write_bytes(candidate.read_bytes())
        result = gate.release(types.SimpleNamespace(job_dir=str(self.job_dir), review=str(review)))
        self.assertEqual(result["approved_sha256"], gate.digest(orphan))
        self.assertTrue((approved_dir / "release.json").exists())

    def test_changed_candidate_receipt_or_contract_blocks_release(self):
        candidate = self.candidate()
        review = self.review(candidate)
        candidate.write_bytes(png_bytes("#0a0a0a"))
        with self.assertRaisesRegex(gate.GateError, "differs from receipt"):
            gate.release(types.SimpleNamespace(job_dir=str(self.job_dir), review=str(review)))

    def test_prepare_generate_release_on_local_provider(self):
        self.prepare()
        calls = []
        image_data = png_bytes("#d31c39")

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def do_POST(self):
                body = self.rfile.read(int(self.headers["Content-Length"]))
                calls.append({"path": self.path, "body": body})
                payload = json.dumps({"data": [{"b64_json": base64.b64encode(image_data).decode("ascii")}]}) .encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)

        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            env = {"MEDIA_API_BASE_URL": f"http://127.0.0.1:{server.server_port}/v1",
                   "MEDIA_API_KEY": "test-only", "MEDIA_API_ALLOW_LOOPBACK_HTTP": "1"}
            with patch.dict(gate.os.environ, env), redirect_stdout(io.StringIO()):
                code = gate.generate(types.SimpleNamespace(job_dir=str(self.job_dir)))
            self.assertEqual(code, 0)
            self.assertEqual(len(calls), 1)
            self.assertEqual(calls[0]["path"], "/v1/images/edits")
            candidate = self.job_dir / "candidate.png"
            review = self.review(candidate)
            gate.release(types.SimpleNamespace(job_dir=str(self.job_dir), review=str(review)))
            self.assertEqual(gate.verify(types.SimpleNamespace(job_dir=str(self.job_dir)))["sha256"],
                             gate.digest(candidate))
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)


if __name__ == "__main__":
    unittest.main()
