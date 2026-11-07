"""Fail-closed SKU contract gate for image jobs and approved downstream assets.

The contract is approved by a product owner. Image appearance still requires
human inspection; this program checks provenance, completeness and release state.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import uuid

from PIL import Image


class GateError(Exception):
    pass


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise GateError(f"Cannot read JSON: {path}") from exc
    if not isinstance(value, dict):
        raise GateError(f"Expected JSON object: {path}")
    return value


def write_new(path: Path, value: dict | str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    contents = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, indent=2) + "\n"
    try:
        with path.open("x", encoding="utf-8", newline="") as handle:
            handle.write(contents)
    except FileExistsError as exc:
        raise GateError(f"Existing file will not be overwritten: {path}") from exc


def verify_image(path: Path) -> None:
    try:
        with Image.open(path) as im:
            im.verify()
        with Image.open(path) as im:
            im.load()
    except (OSError, ValueError) as exc:
        raise GateError(f"Image cannot be decoded: {path}") from exc


def _require_text(value: object, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise GateError(f"Missing {label}")
    return value.strip()


def _load_contract(path: Path, require_approval: bool = True) -> tuple[dict, dict[str, Path]]:
    contract = read_json(path)
    if contract.get("schema_version") != "1.0":
        raise GateError("Unsupported SKU contract schema")
    for label in ("sku_id", "version"):
        value = _require_text(contract.get(label), label)
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]{0,79}", value):
            raise GateError(f"{label} must be a simple file-safe identifier")
    approval = contract.get("approval")
    if not isinstance(approval, dict):
        raise GateError("Missing approval record")
    if require_approval:
        if approval.get("status") != "APPROVED":
            raise GateError("SKU source facts require product-owner approval")
        _require_text(approval.get("reviewer"), "approval reviewer")
        _require_text(approval.get("approved_at"), "approval timestamp")
    refs = contract.get("references")
    if not isinstance(refs, dict) or set(refs) != {"identity", "product"}:
        raise GateError("An identity and current-product reference are required")
    resolved: dict[str, Path] = {}
    for role in ("identity", "product"):
        item = refs[role]
        if not isinstance(item, dict):
            raise GateError(f"Invalid {role} reference")
        rel = _require_text(item.get("path"), f"{role} path")
        ref = (path.parent / rel).resolve()
        if not ref.is_file():
            raise GateError(f"Missing {role} reference: {ref}")
        verify_image(ref)
        expected = _require_text(item.get("sha256"), f"{role} sha256")
        if digest(ref) != expected:
            raise GateError(f"Changed {role} reference; approve a new SKU version")
        resolved[role] = ref
    features = contract.get("must_preserve")
    if not isinstance(features, list) or not features:
        raise GateError("At least one product feature is required")
    ids = set()
    for feature in features:
        if not isinstance(feature, dict):
            raise GateError("Invalid feature")
        feature_id = _require_text(feature.get("id"), "feature id")
        _require_text(feature.get("description"), "feature description")
        _require_text(feature.get("source_evidence"), "feature source_evidence")
        if feature_id in ids:
            raise GateError(f"Duplicate feature: {feature_id}")
        ids.add(feature_id)
    blocked = contract.get("unknown_or_unverified")
    if not isinstance(blocked, list) or any(not isinstance(x, str) or not x.strip() for x in blocked):
        raise GateError("unknown_or_unverified must be a list of nonempty strings")
    return contract, resolved


def _prompt(contract: dict) -> str:
    facts = "\n".join(f"- {item['description']}" for item in contract["must_preserve"])
    unknown = "\n".join(f"- {item}" for item in contract["unknown_or_unverified"])
    return ("图片 1 仅锁定人物身份，不继承其旧衣服。图片 2 是当前 SKU 的商品实拍，"
            "优先保留其可见结构，不从生成图或人物参考推断商品事实。\n"
            f"SKU: {contract['sku_id']}，版本: {contract['version']}。\n"
            f"必须保留的商品特征：\n{facts}\n"
            f"以下事实未获证实，不得自行补造或宣称准确：\n{unknown or '- 无'}\n"
            "姿态、背景及构图以任务要求为准；不得遮挡本镜必须核对的商品部位。"
            "生成结果仅是待审核候选图，需逐项与商品原图核对。\n"
            f"用途与画面要求：{contract.get('creative_brief', '清晰展示当前商品。')}\n")


def prepare(args: argparse.Namespace) -> dict:
    spec_path = Path(args.spec).resolve()
    contract, refs = _load_contract(spec_path)
    job_dir = Path(args.job_dir).resolve()
    prompt_path = job_dir / "prompt.txt"
    plan_path = job_dir / "sku-job.json"
    if prompt_path.exists() or plan_path.exists() or (job_dir / "candidate.receipt.json").exists():
        raise GateError("Job already exists; use a new job directory")
    prompt = _prompt(contract)
    plan = {"schema_version": "1.0", "status": "PREPARED",
            "sku_id": contract["sku_id"], "sku_version": contract["version"],
            "contract_path": str(spec_path), "contract_sha256": digest(spec_path),
            "reference_paths": {role: str(ref) for role, ref in refs.items()},
            "reference_sha256": {role: digest(ref) for role, ref in refs.items()},
            "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
            "model": _require_text(args.model, "model"), "size": _require_text(args.size, "size"),
            "quality": _require_text(args.quality, "quality"),
            "candidate_output": str(job_dir / "candidate.png"),
            "feature_ids": [item["id"] for item in contract["must_preserve"]]}
    write_new(prompt_path, prompt)
    write_new(plan_path, plan)
    return plan


def _load_plan(job_dir: Path) -> tuple[dict, dict]:
    plan = read_json(job_dir / "sku-job.json")
    if plan.get("schema_version") != "1.0" or plan.get("status") != "PREPARED":
        raise GateError("Invalid SKU job")
    spec_path = Path(plan["contract_path"])
    if digest(spec_path) != plan["contract_sha256"]:
        raise GateError("SKU contract changed after preparation")
    contract, refs = _load_contract(spec_path)
    if (contract["sku_id"] != plan["sku_id"] or contract["version"] != plan["sku_version"] or
            [item["id"] for item in contract["must_preserve"]] != plan["feature_ids"]):
        raise GateError("SKU facts changed after preparation")
    for role, ref in refs.items():
        if str(ref) != plan["reference_paths"][role] or digest(ref) != plan["reference_sha256"][role]:
            raise GateError("SKU references changed after preparation")
    if digest(job_dir / "prompt.txt") != plan["prompt_sha256"]:
        raise GateError("Prompt changed after preparation")
    if Path(plan["candidate_output"]).parent != job_dir:
        raise GateError("Candidate output is outside its job directory")
    return plan, contract


def generate(args: argparse.Namespace) -> int:
    job_dir = Path(args.job_dir).resolve()
    plan, _ = _load_plan(job_dir)
    output = Path(plan["candidate_output"])
    if any(job_dir.glob("candidate.*")):
        raise GateError("Candidate or receipt already exists; reconcile this attempt before retrying")
    cmd = [sys.executable, str(Path(__file__).with_name("media_api.py")), "edit",
           "--model", plan["model"], "--prompt-file", str(job_dir / "prompt.txt"),
           "--reference", plan["reference_paths"]["identity"],
           "--reference", plan["reference_paths"]["product"],
           "--size", plan["size"], "--quality", plan["quality"],
           "--output", str(output)]
    completed = subprocess.run(cmd, check=False, capture_output=True, text=True, errors="replace")
    if completed.stdout:
        print(completed.stdout, end="")
    if completed.stderr:
        print(completed.stderr, end="", file=sys.stderr)
    return completed.returncode


def _candidate(job_dir: Path, plan: dict) -> tuple[Path, dict]:
    output = Path(plan["candidate_output"])
    receipt = read_json(output.with_suffix(".receipt.json"))
    if receipt.get("status") != "TECHNICAL_SUCCESS":
        raise GateError("Candidate has no technical success receipt")
    image = receipt.get("image")
    if not isinstance(image, dict) or not isinstance(image.get("file"), str):
        raise GateError("Receipt has no image")
    candidate = (job_dir / image["file"]).resolve()
    if candidate.parent != job_dir or not candidate.is_file():
        raise GateError("Candidate image missing")
    verify_image(candidate)
    if digest(candidate) != image.get("sha256"):
        raise GateError("Candidate image differs from receipt")
    if (receipt.get("model") != plan["model"] or receipt.get("prompt_sha256") != plan["prompt_sha256"] or
            receipt.get("requested_size") != plan["size"] or receipt.get("requested_quality") != plan["quality"] or
            [r.get("sha256") for r in receipt.get("reference_images", [])] !=
            [plan["reference_sha256"]["identity"], plan["reference_sha256"]["product"]]):
        raise GateError("Candidate receipt does not match SKU job")
    return candidate, receipt


def release(args: argparse.Namespace) -> dict:
    job_dir = Path(args.job_dir).resolve()
    plan, _ = _load_plan(job_dir)
    candidate, receipt = _candidate(job_dir, plan)
    review = read_json(Path(args.review))
    reviewer = _require_text(review.get("reviewer"), "reviewer")
    checks = review.get("checks")
    if not isinstance(checks, dict) or set(checks) != set(plan["feature_ids"]):
        raise GateError("Review must cover every SKU feature exactly once")
    for feature_id, result in checks.items():
        if not isinstance(result, dict) or result.get("status") != "PASS":
            raise GateError(f"Feature not approved: {feature_id}")
        _require_text(result.get("evidence_note"), f"{feature_id} evidence_note")
    if review.get("unknowns_not_claimed") is not True:
        raise GateError("Reviewer must confirm unknown facts were not presented as verified")
    if review.get("candidate_sha256") != digest(candidate):
        raise GateError("Review is for a different candidate image")
    approved_dir = job_dir / "approved"
    approved_dir.mkdir(exist_ok=True)
    approved = approved_dir / f"{plan['sku_id']}-{plan['sku_version']}{candidate.suffix}"
    if (approved_dir / "release.json").exists():
        raise GateError("Approved release already exists")
    if approved.is_symlink():
        raise GateError("Approved output is a symlink")
    if approved.exists() and (not approved.is_file() or digest(approved) != digest(candidate)):
        raise GateError("Approved output name is occupied by different content")
    temporary = approved_dir / (".pending-" + uuid.uuid4().hex)
    try:
        with candidate.open("rb") as source, temporary.open("xb") as dest:
            shutil.copyfileobj(source, dest)
            dest.flush()
            os.fsync(dest.fileno())
        if digest(temporary) != digest(candidate):
            raise GateError("Approved copy differs from candidate")
        if not approved.exists():
            os.link(temporary, approved)
        manifest = {"schema_version": "1.0", "status": "APPROVED", "sku_id": plan["sku_id"],
                    "sku_version": plan["sku_version"], "contract_sha256": plan["contract_sha256"],
                    "candidate_sha256": digest(candidate), "approved_file": approved.name,
                    "approved_sha256": digest(approved), "reviewer": reviewer,
                    "review_record_path": str(Path(args.review).resolve()),
                    "review_record_sha256": digest(Path(args.review)), "receipt_run_id": receipt.get("run_id")}
        write_new(approved_dir / "release.json", manifest)
        return manifest
    finally:
        temporary.unlink(missing_ok=True)


def verify(args: argparse.Namespace) -> dict:
    job_dir = Path(args.job_dir).resolve()
    plan, _ = _load_plan(job_dir)
    release_record = read_json(job_dir / "approved" / "release.json")
    if release_record.get("status") != "APPROVED" or release_record.get("contract_sha256") != plan["contract_sha256"]:
        raise GateError("Approved release does not match current SKU")
    review_path = Path(release_record["review_record_path"])
    if digest(review_path) != release_record.get("review_record_sha256"):
        raise GateError("Approval review changed after release")
    approved = (job_dir / "approved" / release_record["approved_file"]).resolve()
    if approved.parent != job_dir / "approved" or not approved.is_file():
        raise GateError("Approved image missing")
    verify_image(approved)
    if digest(approved) != release_record.get("approved_sha256"):
        raise GateError("Approved image changed")
    return {"approved_file": str(approved), "sku_id": plan["sku_id"],
            "sku_version": plan["sku_version"], "sha256": digest(approved)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("prepare")
    p.add_argument("--spec", required=True)
    p.add_argument("--job-dir", required=True)
    p.add_argument("--model", required=True)
    p.add_argument("--size", required=True)
    p.add_argument("--quality", required=True)
    for name in ("generate", "verify"):
        sub.add_parser(name).add_argument("--job-dir", required=True)
    p = sub.add_parser("release")
    p.add_argument("--job-dir", required=True)
    p.add_argument("--review", required=True)
    args = parser.parse_args()
    try:
        if args.command == "generate":
            return generate(args)
        result = {"prepare": prepare, "release": release, "verify": verify}[args.command](args)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (GateError, OSError, KeyError, TypeError) as exc:
        print(f"SKU gate stopped: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
