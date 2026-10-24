"""F28/F29/F30/F31/F32 and site masking [P1/P2]; lab-taxonomy runs, no BLAST needed."""

import shutil
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from biotrace_core.audit import read_run, verify_run
from biotrace_core.config import DEFAULT_RULES, load_rules
from biotrace_core.pipeline import run_analysis
from biotrace_core.records import (
    add_note,
    aggregate_gaps,
    compare_runs,
    find_by_fingerprint,
    load_notes,
    propose_sequences,
    rematch,
    site_points,
)
from biotrace_core.reference.store import load_reference
from scripts.make_demo_data import create_demo


def lab_run(demo: Path, out: Path, rules: Path = DEFAULT_RULES):
    return run_analysis(
        demo / "reads_SIMULASI.csv",
        demo / "metadata_SIMULASI.csv",
        None,
        demo / "taxonomy_SIMULASI.csv",
        None,
        demo / "reference_SIMULASI",
        rules,
        out,
        "simulation",
    )


@pytest.fixture(scope="module")
def demo(tmp_path_factory):
    return create_demo(tmp_path_factory.mktemp("demo") / "SIMULASI")


@pytest.fixture
def runs(tmp_path, demo):
    out = tmp_path / "runs"
    result = lab_run(demo, out)
    return result, out


def test_F28_verify_code_full_and_prefix(runs):
    result, out = runs
    code = result.manifest.report_fingerprint
    for value in (code, code[:12], code.upper()):
        found = find_by_fingerprint(out, value)
        assert found["found"] and found["valid"] and found["run_id"] == result.run_id
    assert find_by_fingerprint(out, "0" * 64)["found"] is False


def test_F28_verify_detects_tampering(runs):
    result, out = runs
    claims = out / result.run_id / "claims_SIMULASI.csv"
    claims.write_bytes(claims.read_bytes() + b"\n")
    found = find_by_fingerprint(out, result.manifest.report_fingerprint)
    assert found["found"] and not found["valid"]
    assert "output_mismatch:claims_SIMULASI.csv" in found["errors"]


def test_F29_notes_append_only_and_outside_fingerprint(runs):
    result, out = runs
    folder = out / result.run_id
    claim_id = result.claims[0].claim_id
    add_note(folder, claim_id, "Ahli A", "Cek ulang voucher.", False)
    add_note(folder, claim_id, "Ahli B", "Sudah dicek.", True)
    notes = load_notes(folder)
    assert [n.reviewer for n in notes] == ["Ahli A", "Ahli B"]
    assert notes[-1].verified is True
    assert verify_run(folder)["valid"]
    assert read_run(folder).manifest.report_fingerprint == result.manifest.report_fingerprint
    with pytest.raises(ValueError):
        add_note(folder, "missing", "Ahli", "x", False)
    with pytest.raises(ValueError):
        add_note(folder, claim_id, " ", "x", False)


def test_P1_site_points_mask_sensitive_sites(runs):
    result, out = runs
    points = site_points(out / result.run_id, decimals=1)
    sensitive = {
        c.site_id
        for c in result.claims
        if {"threatened", "endemic", "possible_endemic"} & set(c.labels)
    }
    assert points and {p.site_id for p in points} == {c.site_id for c in result.claims}
    for point in points:
        assert point.masked == (point.site_id in sensitive)
        if point.masked:
            assert point.latitude == round(point.latitude, 1)
            assert point.longitude == round(point.longitude, 1)
        assert sum(point.decisions.values()) == sum(
            c.site_id == point.site_id for c in result.claims
        )


def test_F32_compare_and_rematch_across_rules(runs, demo, tmp_path):
    result, out = runs
    assert compare_runs(result, result).changes == []
    old_rules = DEFAULT_RULES.parent / "rules_r0.2.yaml"
    other, diff = rematch(
        out / result.run_id, demo / "reference_SIMULASI", old_rules, tmp_path / "rematch"
    )
    assert other.manifest.rules_version == "r0.2"
    assert diff.base_rules_version == load_rules().rules_version
    assert diff.unchanged + len(diff.changes) == len(result.claims)
    for change in diff.changes:  # r0.3 → r0.2 can only drop the D-030 label
        assert change.change == "changed"
        assert "possible_endemic" in change.before["labels"]
        assert "possible_endemic" not in change.after["labels"]


def test_F30_aggregate_gaps_never_mixes_real_and_simulated(runs, demo, tmp_path):
    result, out = runs
    rows = aggregate_gaps([out / result.run_id, out / result.run_id])
    assert rows and all(r["runs"] == 2 and r["is_simulated"] for r in rows)
    assert {"waterbody_id", "name_or_asv", "max_score", "reasons"} <= rows[0].keys()
    assert not {"sites", "total_reads"} & rows[0].keys()


def test_F31_proposal_is_dry_run(demo, tmp_path):
    cfg = load_rules()
    ref_dir = demo / "reference_SIMULASI"
    before = sorted(p.name for p in ref_dir.iterdir())
    source = load_reference(ref_dir, "simulation").select(cfg, "simulation", "12S_MiFish_U")
    fasta = tmp_path / "new.fasta"
    meta = tmp_path / "new.csv"
    shutil.copyfile(ref_dir / "sequences_SIMULASI.fasta", fasta)
    text = (ref_dir / "sequences_SIMULASI.csv").read_text(encoding="utf-8")
    meta.write_text(text, encoding="utf-8")
    summary = propose_sequences(fasta, meta, source, cfg, tmp_path / "proposals")
    assert summary["status"] == "menunggu_kurator"
    assert summary["submitted"] == sum(summary["counts"].values())
    assert (tmp_path / "proposals" / summary["proposal_id"] / "curation_report.csv").is_file()
    assert sorted(p.name for p in ref_dir.iterdir()) == before


def test_API_P1_endpoints(monkeypatch, runs):
    import api.main as api

    result, out = runs
    monkeypatch.setenv("BIOTRACE_RUNS_DIR", str(out))
    client = TestClient(api.app)
    code = result.manifest.report_fingerprint
    assert client.post("/api/verify", json={"report_fingerprint": code[:12]}).json()["valid"]
    assert client.post("/api/verify", json={"report_fingerprint": "xyz"}).status_code == 422
    claim_id = result.claims[0].claim_id
    note = {"reviewer": "Ahli", "note": "Tercatat.", "verified": True}
    response = client.post(f"/api/runs/{result.run_id}/claims/{claim_id}/notes", json=note)
    assert response.status_code == 200, response.text
    assert client.get(f"/api/runs/{result.run_id}/notes").json()[0]["verified"] is True
    assert client.get(f"/api/runs/{result.run_id}/sites").status_code == 200
    compared = client.get(f"/api/runs/{result.run_id}/compare/{result.run_id}").json()
    assert compared["changes"] == []
