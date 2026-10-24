"""T-API/T-SIM/T-REPRO/T-ISO/T-INV [MVP] actual BLAST and report integration."""

import io
import json
import shutil
import zipfile
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from pypdf import PdfReader

from biotrace_core.audit import verify_run
from biotrace_core.io.loaders import read_table
from biotrace_core.naming.blast import executable, match_sequences
from biotrace_core.pipeline import run_analysis
from biotrace_core.reference.store import load_reference
from scripts.make_demo_data import create_demo

pytestmark = pytest.mark.blast


@pytest.fixture(scope="module")
def demo(tmp_path_factory):
    if not executable("blastn"):
        pytest.skip("Installer BLAST+ diperlukan untuk uji integrasi FASTA.")
    return create_demo(tmp_path_factory.mktemp("demo") / "SIMULASI")


def analyze(demo: Path, out: Path, threads: int = 4, lab_only: bool = False):
    return run_analysis(
        demo / "reads_SIMULASI.csv",
        demo / "metadata_SIMULASI.csv",
        None if lab_only else demo / "asv_SIMULASI.fasta",
        demo / "taxonomy_SIMULASI.csv",
        None,
        demo / "reference_SIMULASI",
        out_root=out,
        mode="simulation",
        threads=threads,
    )


@pytest.fixture(scope="module")
def completed(demo, tmp_path_factory):
    out = tmp_path_factory.mktemp("completed")
    return analyze(demo, out), out


def test_T_SIM_SCN_all_16_expected_decisions(completed, demo):
    run, _ = completed
    expected = {
        r["asv_id"]: r["expected_decision"] for r in read_table(demo / "scenarios_SIMULASI.csv")
    }
    assert len(run.claims) == 32
    assert len(expected) == 16
    assert all(c.decision == expected[c.asv_id] for c in run.claims)
    assert all(d.claims >= 2 for d in run.summary.decisions)
    assert all(c.reported_rank == "genus" for c in run.claims if c.asv_id == "SIM_ASV_014")


def test_T_INV_limits_labels_and_reasons(completed):
    run, _ = completed
    for claim in run.claims:
        assert claim.is_simulated
        assert claim.interpretation_limit in claim.reasons_id
        assert claim.reasons_en
        if claim.grade != "A" or claim.reported_rank != "species":
            assert claim.causes
        if claim.reported_rank == "species":
            assert claim.best_pct >= 98
        if "endemic" in claim.labels and claim.grade in {"C", "D"}:
            assert claim.decision == "must_verify"


def test_R_AUD_01_04_actual_threads_reproduce(completed, demo, tmp_path):
    original, _ = completed
    other = analyze(demo, tmp_path, threads=1)
    assert other.manifest.execution["blast_threads"] == 1
    assert other.manifest.report_fingerprint == original.manifest.report_fingerprint
    assert other.manifest.run_fingerprint == original.manifest.run_fingerprint
    assert verify_run(tmp_path / other.run_id)["valid"]


def test_R_AUD_04_changed_input_changes_identity(completed, demo, tmp_path):
    copy = tmp_path / "input_SIMULASI"
    shutil.copytree(demo, copy)
    path = copy / "reads_SIMULASI.csv"
    path.write_bytes(path.read_bytes() + b"\n")
    changed = analyze(copy, tmp_path / "runs")
    assert changed.manifest.run_fingerprint != completed[0].manifest.run_fingerprint


def test_R_AUD_verify_detects_output_and_payload_tampering(completed, tmp_path):
    run, root = completed
    target = tmp_path / run.run_id
    shutil.copytree(root / run.run_id, target)
    csv = target / "claims_SIMULASI.csv"
    csv.write_bytes(csv.read_bytes() + b"tampered\n")
    assert not verify_run(target)["valid"]
    target2 = tmp_path / "payload"
    shutil.copytree(root / run.run_id, target2)
    payload = target2 / "run_result_SIMULASI.json"
    data = json.loads(payload.read_text(encoding="utf-8"))
    data["summary"]["total_claims"] = 999
    payload.write_text(json.dumps(data), encoding="utf-8")
    assert "result_payload_mismatch" in verify_run(target2)["errors"]


def test_F24_PDF_every_page_simulation_limit_and_footer(completed):
    run, root = completed
    reader = PdfReader(root / run.run_id / "report_SIMULASI.pdf")
    assert len(reader.pages) >= 6
    for page in reader.pages:
        text = page.extract_text()
        assert "SIMULASI" in text
        assert "Bukan dokumen AMDAL resmi" in text
        assert "Deteksi DNA bukan bukti pasti" in text
    text = "\n".join(page.extract_text() for page in reader.pages)
    assert run.manifest.report_fingerprint in text.replace("\n", "")
    assert "Sumber dan lisensi" in text


def test_R_NAME_12_lab_mode_pipeline(demo, tmp_path):
    run = analyze(demo, tmp_path, lab_only=True)
    assert all(c.assessed_with_lab_database for c in run.claims)
    assert all(c.voucher_support is None for c in run.claims)


def test_R_NAME_02_windows_space_path_and_no_V4(demo, tmp_path, cfg):
    ref = load_reference(demo / "reference_SIMULASI", "simulation").select(
        cfg, "simulation", "12S_MiFish_U"
    )
    bad = ref.sequences[0].model_copy(update={"voucher_level": "V4", "seq_id": "V4_FORBIDDEN"})
    ref.sequences.append(bad)
    ref.fasta[bad.seq_id] = ref.fasta[ref.sequences[0].seq_id]
    ref = ref.select(cfg, "simulation", "12S_MiFish_U")
    folder = tmp_path / "folder with spaces"
    result, _ = match_sequences({"SIM": next(iter(ref.fasta.values()))}, ref, cfg, folder)
    assert result
    assert "V4_FORBIDDEN" not in (folder / "blast_input.fasta").read_text()


def test_T_API_full_workflow_and_security(monkeypatch, tmp_path, completed):
    from api.main import app

    monkeypatch.setenv("BIOTRACE_RUNS_DIR", str(tmp_path / "runs"))
    client = TestClient(app)
    assert client.get("/api/health").status_code == 200
    response = client.post("/api/runs/demo/matano_sim_v3")
    assert response.status_code == 200, response.text
    run_id = response.json()["run_id"]
    run = client.get(f"/api/runs/{run_id}").json()
    assert len(run["claims"]) == 32
    claims = client.get(f"/api/runs/{run_id}/claims?decision=must_verify&limit=2").json()
    assert len(claims) == 2 and all(c["decision"] == "must_verify" for c in claims)
    assert client.get(f"/api/runs/{run_id}/claims/{claims[0]['claim_id']}").status_code == 200
    assert client.get(f"/api/runs/{run_id}/coverage").status_code == 200
    assert client.get(f"/api/runs/{run_id}/barcode-priority").status_code == 200
    assert client.get(f"/api/runs/{run_id}/report.pdf").content.startswith(b"%PDF")
    export = client.get(f"/api/runs/{run_id}/export.zip")
    with zipfile.ZipFile(io.BytesIO(export.content)) as z:
        assert len(z.namelist()) == 6
        assert all("SIMULASI" in name for name in z.namelist())
    assert client.get("/api/runs/INVALID/claims").status_code == 404
    assert client.get("/api/runs/demo/claims").status_code == 404
    assert client.post("/api/runs/demo/missing").status_code == 404
    assert client.post("/api/runs", headers={"content-length": str(2 * 1024**3)}).status_code == 413
    assert client.get("/api/does-not-exist").status_code == 404


def test_T_API_upload_detection_and_invalid_file(monkeypatch, tmp_path, demo):
    from api.main import app

    monkeypatch.setenv("BIOTRACE_RUNS_DIR", str(tmp_path / "runs"))
    client = TestClient(app)
    files = {
        role: (filename, (demo / filename).read_bytes())
        for role, filename in [
            ("reads", "reads_SIMULASI.csv"),
            ("metadata", "metadata_SIMULASI.csv"),
            ("fasta", "asv_SIMULASI.fasta"),
        ]
    }
    response = client.post("/api/runs", files=files, data={"mode": "simulation"})
    assert response.status_code == 200, response.text
    assert response.json()["is_simulated"]
    files["reads"] = ("evil.exe", b"bad")
    assert client.post("/api/runs", files=files, data={"mode": "simulation"}).status_code == 422


def test_T_API_no_blast_fallback_verified_only(monkeypatch, tmp_path, completed):
    import api.main as api

    monkeypatch.setenv("BIOTRACE_RUNS_DIR", str(tmp_path / "runs"))
    monkeypatch.setattr(api, "executable", lambda _: None)
    client = TestClient(api.app)
    # A precomputed result is prepared from a real pipeline run, never hand-authored.
    run, root = completed
    target = tmp_path / "precomputed/matano_SIMULASI_v3"
    target.parent.mkdir()
    shutil.copytree(root / run.run_id, target)
    monkeypatch.setattr(api, "ROOT", tmp_path)
    response = client.post("/api/runs/demo/matano_sim_v3")
    assert response.status_code == 200, response.text
    assert response.json()["precomputed"] is True
    assert verify_run(tmp_path / "runs" / run.run_id)["valid"]
