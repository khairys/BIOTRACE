"""D-038 [MVP]: failures, immutable upgrade, and source-bound reports."""

import io
import subprocess
from pathlib import Path

import pytest

from biotrace_core.audit import read_run, verify_run
from biotrace_core.cli import parser
from biotrace_core.config import DEFAULT_REFERENCE, ROOT, blast_timeout, load_rules
from biotrace_core.demo import REAL_PRECOMPUTED_NAME, REAL_PROVENANCE, REAL_REF
from biotrace_core.naming import blast
from biotrace_core.reference.store import load_reference


def test_D038_defaults_share_v05(monkeypatch):
    from api.main import reference_root

    monkeypatch.delenv("BIOTRACE_REF_DIR", raising=False)
    args = parser().parse_args(["run", "--reads", "r.csv", "--meta", "m.csv"])
    assert args.ref == reference_root() == REAL_REF == DEFAULT_REFERENCE
    assert DEFAULT_REFERENCE.name == "v0.5"


@pytest.mark.parametrize("value", ["0", "-1", "3601", "invalid"])
def test_D038_invalid_execution_budget_is_explicit(monkeypatch, value):
    monkeypatch.setenv("BIOTRACE_BLAST_TIMEOUT_SECONDS", value)
    with pytest.raises(ValueError, match="1–3600"):
        blast_timeout()


def test_R_NAME_02_timeout_is_actionable_without_partial_hits(monkeypatch, tmp_path, ref, cfg):
    monkeypatch.setenv("BIOTRACE_BLAST_TIMEOUT_SECONDS", "7")
    monkeypatch.setattr(blast, "build_database", lambda _ref, _folder: Path("ref"))
    monkeypatch.setattr(blast, "executable", lambda _name: "blastn")
    budgets = []

    def timeout(*args, **kwargs):
        budgets.append(kwargs["timeout"])
        raise subprocess.TimeoutExpired(args[0], kwargs["timeout"])

    monkeypatch.setattr(blast.subprocess, "run", timeout)
    with pytest.raises(ValueError, match="Hasil parsial tidak diterbitkan"):
        blast.match_sequences({"SIMULASI": "ACGT"}, ref, cfg, tmp_path)
    assert budgets == [7]


def test_R_NAME_02_database_timeout_is_structured(monkeypatch, tmp_path, ref):
    monkeypatch.setattr(blast, "executable", lambda _name: "makeblastdb")

    def timeout(*args, **kwargs):
        raise subprocess.TimeoutExpired(args[0], kwargs["timeout"])

    monkeypatch.setattr(blast.subprocess, "run", timeout)
    with pytest.raises(ValueError, match="Pembuatan database BLAST melewati"):
        blast.build_database(ref, tmp_path)


def test_D038_v05_preserves_all_old_evidence():
    cfg = load_rules()
    previous = load_reference(ROOT / "data/reference/v0.4").select(
        cfg, "normal", cfg.marker_default
    )
    current = load_reference(DEFAULT_REFERENCE).select(cfg, "normal", cfg.marker_default)
    records = {r.seq_id: r for r in current.eligible}
    for record in previous.eligible:
        assert records[record.seq_id] == record
        assert current.fasta[record.seq_id] == previous.fasta[record.seq_id]
    assert len(current.eligible) - len(previous.eligible) == 33
    assert all(r.voucher_level != "V4" for r in current.eligible)


def test_D038_rules_keep_lf_for_cross_platform_fingerprints():
    for path in (ROOT / "biotrace_core/rules").glob("*.yaml"):
        assert b"\r\n" not in path.read_bytes()


def test_D038_old_precomputed_remains_verifiable():
    for path in (ROOT / "precomputed").iterdir():
        if path.is_dir() and path.name != REAL_PRECOMPUTED_NAME:
            assert verify_run(path)["valid"], path


def test_D038_real_demo_is_complete_and_provenance_bound():
    path = ROOT / "precomputed" / REAL_PRECOMPUTED_NAME
    assert path.is_dir(), "Jalankan scripts/prepare_jury.py precompute sebelum rilis."
    assert verify_run(path)["valid"]
    result = read_run(path)
    assert result.manifest.reference_version == "v0.5"
    assert result.manifest.parameters["data_provenance"] == REAL_PROVENANCE.model_dump(mode="json")
    assert result.summary.total_claims == 4354
    assert not result.summary.is_simulated
    assert all(c.interpretation_limit and not c.is_simulated for c in result.claims)


def test_D038_real_demo_without_blast_uses_verified_v05(monkeypatch, tmp_path):
    from fastapi.testclient import TestClient

    import api.main as api

    monkeypatch.setenv("BIOTRACE_RUNS_DIR", str(tmp_path))
    monkeypatch.setattr(api, "executable", lambda _name: None)
    response = TestClient(api.app).post(f"/api/runs/demo/{api.REAL_DEMO_ID}")
    assert response.status_code == 200
    assert response.json()["precomputed"] is True
    assert response.json()["is_simulated"] is False
    result = read_run(tmp_path / response.json()["run_id"])
    assert result.manifest.reference_version == "v0.5"
    assert verify_run(tmp_path / result.run_id)["valid"]


def test_D038_changed_local_demo_is_rejected(monkeypatch, tmp_path):
    from fastapi import HTTPException

    import api.main as api

    source = ROOT / "precomputed/matano_SIMULASI_v3_r0.4"
    monkeypatch.setenv("BIOTRACE_RUNS_DIR", str(tmp_path))
    result = api._from_precomputed(source)
    claims = tmp_path / result.run_id / "claims_SIMULASI.csv"
    claims.write_bytes(claims.read_bytes() + b"changed\n")
    with pytest.raises(HTTPException) as failure:
        api._from_precomputed(source)
    assert failure.value.status_code == 409


def test_D038_concurrent_demo_imports_publish_one_complete_run(monkeypatch, tmp_path):
    from concurrent.futures import ThreadPoolExecutor

    import api.main as api

    source = ROOT / "precomputed/matano_SIMULASI_v3_r0.4"
    monkeypatch.setenv("BIOTRACE_RUNS_DIR", str(tmp_path))
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(api._from_precomputed, [source, source]))
    assert results[0].run_id == results[1].run_id
    assert verify_run(tmp_path / results[0].run_id)["valid"]


def test_F24_D038_brief_pdf_is_bounded_and_explicit(monkeypatch, tmp_path):
    from fastapi.testclient import TestClient
    from pypdf import PdfReader

    import api.main as api

    monkeypatch.setenv("BIOTRACE_RUNS_DIR", str(tmp_path))
    source = ROOT / "precomputed" / REAL_PRECOMPUTED_NAME
    result = api._from_precomputed(source)
    response = TestClient(api.app).get(f"/api/runs/{result.run_id}/summary.pdf")
    assert response.status_code == 200
    reader = PdfReader(io.BytesIO(response.content))
    assert len(reader.pages) < 30
    text = "\n".join(page.extract_text() for page in reader.pages)
    assert "RINGKASAN PEMERIKSAAN" in text
    assert "4354" in text and "10.5068/D12T1B" in text
    assert result.manifest.report_fingerprint in text.replace("\n", "")
    assert all("Deteksi DNA bukan bukti pasti" in page.extract_text() for page in reader.pages)
    assert verify_run(tmp_path / result.run_id)["valid"]


def test_R_VAL_02_checkpoint_resumes_only_complete_species(monkeypatch, tmp_path, demo_dir):
    import biotrace_core.validation.loso as loso

    cfg = load_rules()
    source = demo_dir / "reference_SIMULASI"
    ref = load_reference(source, "simulation").select(cfg, "simulation", cfg.marker_default)
    names = sorted(ref.available_species)[:2]
    second_ids = {r.seq_id for r in ref.eligible if r.species_valid == names[1]}
    monkeypatch.setattr(loso, "blast_version", lambda: "TEST-SIMULASI")

    def interrupted(query, *_args):
        if second_ids & query.keys():
            raise ValueError("Interupsi uji SIMULASI")
        return {}, ""

    monkeypatch.setattr(loso, "match_sequences", interrupted)
    output = tmp_path / "loso_SIMULASI.json"
    with pytest.raises(ValueError, match="Interupsi"):
        loso.run_loso(source, output, max_species=2)
    assert not output.exists()
    assert output.with_suffix(".checkpoint").exists()
    queries_seen = []

    def successful(query, *_args):
        queries_seen.extend(query)
        return {}, ""

    monkeypatch.setattr(loso, "match_sequences", successful)
    resumed = loso.run_loso(source, output, max_species=2)
    assert set(queries_seen) <= second_ids
    assert not output.with_suffix(".checkpoint").exists()
    complete = loso.run_loso(source, tmp_path / "uninterrupted_SIMULASI.json", max_species=2)
    assert resumed["counts"] == complete["counts"]
    assert resumed["metrics"] == complete["metrics"]
