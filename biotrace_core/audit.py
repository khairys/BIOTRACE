"""R-AUD-01..04 offline SHA-256 and analytical/execution separation [MVP]."""

import hashlib
import json
from pathlib import Path

from biotrace_core.models import Claim, RunResult
from biotrace_core.report.csv_export import artifact_name, canonical_csv


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def fingerprint(value: dict) -> str:
    """R-AUD-02: no timestamps or execution-only parameters."""
    return sha256(
        json.dumps(
            value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
        ).encode("utf-8")
    )


def report_fingerprint(claims_csv: bytes, run_fingerprint: str) -> str:
    """R-AUD-03/04: canonical claims plus analytical run identity."""
    return sha256(claims_csv + run_fingerprint.encode("ascii"))


def read_run(folder: Path) -> RunResult:
    for simulated in (False, True):
        path = folder / artifact_name("run_result", "json", simulated)
        if path.is_file():
            return RunResult.model_validate_json(path.read_bytes())
    raise FileNotFoundError("Hasil run tidak ditemukan.")


def verify_run(folder: Path) -> dict:
    """F4: verify canonical claims AND every saved output/input, not just a supplied hash."""
    result = read_run(folder)
    manifest = result.manifest
    errors = []
    simulated = result.summary.is_simulated
    saved_manifest = json.loads(
        (folder / artifact_name("run_manifest", "json", simulated)).read_bytes()
    )
    if saved_manifest != manifest.model_dump(mode="json"):
        errors.append("manifest_mismatch")
    identity = {
        "input_hashes": manifest.input_hashes,
        "reference_version": manifest.reference_version,
        "reference_manifest_hash": manifest.reference_manifest_hash,
        "rules_version": manifest.rules_version,
        "rules_hash": manifest.rules_hash,
        "reasons_hash": manifest.reasons_hash,
        "engine_version": manifest.engine_version,
        "blast_version": manifest.blast_version,
        "parameters": manifest.parameters,
        "mode": manifest.mode,
    }
    if fingerprint(identity) != manifest.run_fingerprint:
        errors.append("run_fingerprint_mismatch")
    csv_data = canonical_csv(result.claims, sorted(Claim.model_fields))
    if (
        fingerprint(result.model_dump(mode="json", exclude={"manifest"}))
        != manifest.result_payload_hash
    ):
        errors.append("result_payload_mismatch")
    if report_fingerprint(csv_data, manifest.run_fingerprint) != manifest.report_fingerprint:
        errors.append("report_fingerprint_mismatch")
    for name, digest in manifest.output_hashes.items():
        if (
            Path(name).name != name
            or not (folder / name).is_file()
            or sha256((folder / name).read_bytes()) != digest
        ):
            errors.append(f"output_mismatch:{name}")
    for name, digest in manifest.input_hashes.items():
        if (
            Path(name).name != name
            or not (folder / "input" / name).is_file()
            or sha256((folder / "input" / name).read_bytes()) != digest
        ):
            errors.append(f"input_mismatch:{name}")
    return {
        "valid": not errors,
        "report_fingerprint": manifest.report_fingerprint,
        "errors": sorted(errors),
    }
