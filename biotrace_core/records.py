"""Run records outside the analytical fingerprint [P1/P2]: F28, F29, F30, F32, site map.

Nothing here changes claims, scores or decisions; review notes and comparisons are stored
next to a run without being listed in its manifest, so verify_run stays valid.
"""

import json
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path

from biotrace_core.audit import read_run, sha256, verify_run
from biotrace_core.config import RulesConfig
from biotrace_core.io.loaders import read_fasta, read_table, write_table
from biotrace_core.models import Claim, DataProvenance, Model, RunResult
from biotrace_core.pipeline import run_analysis
from biotrace_core.reference.curate import curate_records
from biotrace_core.reference.store import ReferenceIndex
from biotrace_core.report.csv_export import artifact_name

SENSITIVE_LABELS = {"threatened", "endemic", "possible_endemic"}


class ReviewNote(Model):
    claim_id: str
    reviewer: str
    note: str
    verified: bool
    created_at: str


class SitePoint(Model):
    site_id: str
    waterbody_id: str
    latitude: float
    longitude: float
    masked: bool
    decisions: dict[str, int]


class ClaimChange(Model):
    site_id: str
    asv_id: str
    change: str
    before: dict[str, str] | None
    after: dict[str, str] | None


class RunComparison(Model):
    base_run_id: str
    other_run_id: str
    base_reference_version: str
    other_reference_version: str
    base_rules_version: str
    other_rules_version: str
    unchanged: int
    changes: list[ClaimChange]


def run_folders(root: Path) -> list[Path]:
    return sorted(p for p in root.glob("*") if p.is_dir()) if root.is_dir() else []


def find_by_fingerprint(root: Path, report_fingerprint: str) -> dict:
    """F28: look up a report code among runs stored on THIS machine and re-verify it."""
    code = report_fingerprint.strip().lower()
    for folder in run_folders(root):
        try:
            result = read_run(folder)
        except (FileNotFoundError, ValueError):
            continue
        manifest = result.manifest
        if code and code in {manifest.report_fingerprint, manifest.report_fingerprint[:12]}:
            check = verify_run(folder)
            return {
                "found": True,
                "valid": check["valid"],
                "errors": check["errors"],
                "run_id": result.run_id,
                "report_fingerprint": manifest.report_fingerprint,
                "reference_version": manifest.reference_version,
                "rules_version": manifest.rules_version,
                "engine_version": manifest.engine_version,
                "started_at": manifest.started_at,
                "is_simulated": result.summary.is_simulated,
            }
    return {"found": False, "valid": False, "errors": [], "run_id": None}


def notes_path(folder: Path, simulated: bool) -> Path:
    return folder / artifact_name("review_notes", "json", simulated)


def load_notes(folder: Path) -> list[ReviewNote]:
    result = read_run(folder)
    path = notes_path(folder, result.summary.is_simulated)
    if not path.is_file():
        return []
    return [ReviewNote.model_validate(n) for n in json.loads(path.read_text(encoding="utf-8"))]


def add_note(folder: Path, claim_id: str, reviewer: str, note: str, verified: bool) -> ReviewNote:
    """F29: append-only expert note; earlier notes are never edited or removed."""
    result = read_run(folder)
    if claim_id not in {c.claim_id for c in result.claims}:
        raise ValueError("Klaim tidak ditemukan.")
    reviewer, note = reviewer.strip(), note.strip()
    if not reviewer or not note:
        raise ValueError("Nama peninjau dan catatan wajib diisi.")
    if len(reviewer) > 120 or len(note) > 4000:
        raise ValueError("Nama peninjau atau catatan terlalu panjang.")
    entry = ReviewNote(
        claim_id=claim_id,
        reviewer=reviewer,
        note=note,
        verified=verified,
        created_at=datetime.now(UTC).isoformat(timespec="seconds"),
    )
    notes = [n.model_dump() for n in load_notes(folder)] + [entry.model_dump()]
    path = notes_path(folder, result.summary.is_simulated)
    temp = path.with_suffix(".partial")
    temp.write_text(json.dumps(notes, ensure_ascii=False, indent=2), encoding="utf-8")
    temp.replace(path)
    return entry


def site_points(folder: Path, decimals: int = 1) -> list[SitePoint]:
    """Map points; sites with a sensitive claim get coordinates rounded (P1 privacy)."""
    result = read_run(folder)
    stem = artifact_name("metadata", "x", result.summary.is_simulated)[:-2]
    meta = sorted((folder / "input").glob(f"{stem}.*"))
    if not meta:
        return []
    rows = read_table(meta[0])
    counts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    sensitive: set[str] = set()
    for claim in result.claims:
        counts[claim.site_id][claim.decision] += 1
        if SENSITIVE_LABELS & set(claim.labels):
            sensitive.add(claim.site_id)
    points: dict[str, SitePoint] = {}
    for row in sorted(rows, key=lambda r: (r["site_id"], r["sample_id"])):
        site = row["site_id"]
        if site in points or site not in counts:
            continue
        if not row.get("latitude") or not row.get("longitude"):
            continue  # D-036: koordinat tidak tersedia di sumber
        lat, lon = float(row["latitude"]), float(row["longitude"])
        masked = site in sensitive
        if masked:
            lat, lon = round(lat, decimals), round(lon, decimals)
        points[site] = SitePoint(
            site_id=site,
            waterbody_id=row["waterbody_id"],
            latitude=lat,
            longitude=lon,
            masked=masked,
            decisions=dict(sorted(counts[site].items())),
        )
    return list(points.values())


def _claim_view(claim: Claim) -> dict[str, str]:
    return {
        "reported_name": claim.reported_name,
        "reported_rank": claim.reported_rank,
        "grade": claim.grade,
        "decision": claim.decision,
        "labels": ";".join(claim.labels),
    }


def compare_runs(base: RunResult, other: RunResult) -> RunComparison:
    """F32: claims keyed by (site_id, asv_id); report what moved between two runs."""
    before = {(c.site_id, c.asv_id): _claim_view(c) for c in base.claims}
    after = {(c.site_id, c.asv_id): _claim_view(c) for c in other.claims}
    changes, unchanged = [], 0
    for key in sorted(before.keys() | after.keys()):
        a, b = before.get(key), after.get(key)
        if a == b:
            unchanged += 1
            continue
        change = "added" if a is None else "removed" if b is None else "changed"
        changes.append(ClaimChange(site_id=key[0], asv_id=key[1], change=change, before=a, after=b))
    return RunComparison(
        base_run_id=base.run_id,
        other_run_id=other.run_id,
        base_reference_version=base.manifest.reference_version,
        other_reference_version=other.manifest.reference_version,
        base_rules_version=base.manifest.rules_version,
        other_rules_version=other.manifest.rules_version,
        unchanged=unchanged,
        changes=changes,
    )


def rematch(
    folder: Path, reference_dir: Path, rules_path: Path, out_root: Path
) -> tuple[RunResult, RunComparison]:
    """F32: rerun the stored inputs against another reference/rules version, then compare."""
    base = read_run(folder)
    simulated = base.summary.is_simulated
    inputs = folder / "input"

    def stored(role: str) -> Path | None:
        # Inputs keep their original extension (csv/tsv) under a role-based name.
        stem = artifact_name(role, "x", simulated)[:-2]
        found = sorted(p for p in inputs.glob(f"{stem}.*") if p.is_file())
        return found[0] if found else None

    reads, meta = stored("reads"), stored("metadata")
    if reads is None or meta is None:
        raise ValueError("Berkas masukan run tidak lengkap.")
    result = run_analysis(
        reads,
        meta,
        stored("fasta"),
        stored("taxonomy"),
        stored("site_context"),
        reference_dir,
        rules_path,
        out_root,
        base.manifest.mode,
        provenance=DataProvenance.model_validate(base.manifest.parameters["data_provenance"])
        if "data_provenance" in base.manifest.parameters
        else None,
    )
    return result, compare_runs(base, result)


def aggregate_gaps(folders: list[Path]) -> list[dict]:
    """F30: combine barcode priorities across runs the data owners agreed to share.

    Only taxon/waterbody level counts leave a run; samples, reads and coordinates do not.
    Simulated and real runs are never mixed.
    """
    results = [read_run(f) for f in sorted(folders)]
    if len({r.summary.is_simulated for r in results}) > 1:
        raise ValueError("Run SIMULASI dan run nyata tidak boleh digabung.")
    rows: dict[tuple[str, str], dict] = {}
    for result in results:
        for item in result.barcode_priority:
            key = (item.waterbody_id, item.name_or_asv)
            row = rows.setdefault(
                key,
                {
                    "waterbody_id": item.waterbody_id,
                    "name_or_asv": item.name_or_asv,
                    "runs": 0,
                    "max_score": 0,
                    "reasons": set(),
                },
            )
            row["runs"] += 1
            row["max_score"] = max(row["max_score"], item.score)
            row["reasons"] |= set(item.reasons)
    simulated = bool(results) and results[0].summary.is_simulated
    return [
        {**r, "reasons": ";".join(sorted(r["reasons"])), "is_simulated": simulated}
        for _, r in sorted(
            rows.items(), key=lambda kv: (-kv[1]["runs"], -kv[1]["max_score"], kv[0])
        )
    ]


def propose_sequences(
    fasta_path: Path,
    metadata_path: Path,
    source: ReferenceIndex,
    cfg: RulesConfig,
    proposals_root: Path,
) -> dict:
    """F31: collaborator proposal = automatic R-CUR dry run; no reference version is written.

    A curator promotes accepted rows later with `biotrace ref import` (R-CUR-11/12).
    """
    records, _, report = curate_records(
        read_table(metadata_path),
        read_fasta(fasta_path, "ACGTNRYSWKMBDHV"),
        source,
        cfg,
        source.manifest["marker"],
    )
    proposal_id = sha256(fasta_path.read_bytes() + metadata_path.read_bytes())[:12]
    folder = proposals_root / proposal_id
    counts: dict[str, int] = defaultdict(int)
    final = {r["seq_id"]: r["result"] for r in report}  # last step per sequence wins
    for result in final.values():
        counts[result.split(":")[0]] += 1
    summary = {
        "proposal_id": proposal_id,
        "status": "menunggu_kurator",
        "reference_version": source.manifest["reference_version"],
        "rules_version": cfg.rules_version,
        "submitted": len(final),
        "eligible_after_curation": sum(r.curation_status == "accepted" for r in records),
        "counts": dict(sorted(counts.items())),
        "report": report,
        "contains_simulated": bool(source.manifest.get("contains_simulated")),
    }
    if not folder.exists():
        folder.mkdir(parents=True)
        (folder / "sequences.fasta").write_bytes(fasta_path.read_bytes())
        (folder / "metadata.csv").write_bytes(metadata_path.read_bytes())
        write_table(folder / "curation_report.csv", report)
        (folder / "proposal.json").write_text(
            json.dumps({k: v for k, v in summary.items() if k != "report"}, indent=2),
            encoding="utf-8",
        )
    return summary
