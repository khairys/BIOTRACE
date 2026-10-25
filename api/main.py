"""FastAPI local adapter [MVP]; same-origin static React and bounded file input."""

import csv
import io
import json
import logging
import os
import re
import shutil
import tempfile
import zipfile
from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, File, Form, HTTPException, Query, Request, UploadFile
from fastapi.concurrency import run_in_threadpool
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from api.contracts import (
    DatasetsResponse,
    HealthResponse,
    InspectResponse,
    MethodsResponse,
    NoteRequest,
    ProposalResponse,
    ReferenceStats,
    ValidationResults,
    VerifyRequest,
    VerifyResponse,
)
from biotrace_core import __version__
from biotrace_core.audit import read_run, sha256, verify_run
from biotrace_core.config import DEFAULT_REFERENCE, DEFAULT_RULES, ROOT, load_rules
from biotrace_core.demo import REAL_DEMO, REAL_PRECOMPUTED_NAME, REAL_PROVENANCE, REAL_REF
from biotrace_core.io.columns import ALIASES, detect_role, map_table, prepare_metadata
from biotrace_core.io.loaders import read_table
from biotrace_core.io.validate import ALLOWED_EXTENSIONS, MAX_UPLOAD_BYTES, InputError
from biotrace_core.models import (
    BarcodePriorityRow,
    Claim,
    CoverageRow,
    RunCreated,
    RunResult,
)
from biotrace_core.naming.blast import executable
from biotrace_core.pipeline import run_analysis
from biotrace_core.records import (
    ReviewNote,
    RunComparison,
    SitePoint,
    add_note,
    compare_runs,
    find_by_fingerprint,
    load_notes,
    propose_sequences,
    rematch,
    site_points,
)
from biotrace_core.reference.store import load_reference, reference_stats
from biotrace_core.report.csv_export import artifact_name

LOGGER = logging.getLogger("biotrace.api")
app = FastAPI(
    title="BioTrace Indonesia",
    version=__version__,
    description="Laporan verifikasi pendukung data eDNA [MVP]",
)
DEMO = ROOT / "data/demo/matano_SIMULASI_v3"
DEMO_ID = "matano_sim_v3"
# Offline demo fallback is tied to the active rules version (D-030).
PRECOMPUTED_NAME = f"matano_SIMULASI_v3_{load_rules().rules_version}"
# Demo DATA ASLI (D-036): eDNA MiFish-U Marwayana dkk. 2022 (Dryad 10.5068/D12T1B, CC0) + kamus v0.4.
REAL_DEMO_ID = "edna_asli_marwayana2022"


def runs_root() -> Path:
    return Path(os.environ.get("BIOTRACE_RUNS_DIR", str(ROOT / "runs"))).resolve()


def reference_root() -> Path:
    return Path(os.environ.get("BIOTRACE_REF_DIR", str(DEFAULT_REFERENCE))).resolve()


def error_response(
    status: int, code: str, message: str, validation: dict | None = None
) -> JSONResponse:
    return JSONResponse(
        status_code=status,
        content={"error": {"code": code, "message": message, "validation": validation}},
    )


@app.exception_handler(InputError)
async def input_error_handler(request: Request, exc: InputError) -> JSONResponse:
    return error_response(
        422, "VALIDATION_ERROR", "Periksa berkas masukan.", exc.report.model_dump(mode="json")
    )


@app.exception_handler(ValueError)
async def value_error_handler(request: Request, exc: ValueError) -> JSONResponse:
    return error_response(422, "ANALYSIS_ERROR", str(exc))


@app.exception_handler(StarletteHTTPException)
async def http_error_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    return error_response(exc.status_code, "REQUEST_ERROR", str(exc.detail))


@app.exception_handler(RequestValidationError)
async def request_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    return error_response(422, "VALIDATION_ERROR", "Parameter atau file wajib belum lengkap.")


@app.exception_handler(Exception)
async def unexpected_error_handler(request: Request, exc: Exception) -> JSONResponse:
    LOGGER.error("Analisis gagal: %s", type(exc).__name__)
    return error_response(
        500, "INTERNAL_ERROR", "Analisis gagal. Periksa konfigurasi lokal dan log aplikasi."
    )


@app.middleware("http")
async def local_headers(request: Request, call_next):
    length = request.headers.get("content-length", "0")
    if not length.isdigit() or int(length) > MAX_UPLOAD_BYTES * 5:
        return error_response(413, "UPLOAD_TOO_LARGE", "Total unggahan melebihi batas.")
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Cache-Control"] = (
        "no-store" if request.url.path.startswith("/api") else "no-cache"
    )
    return response


def run_folder(run_id: str) -> Path:
    if not re.fullmatch(r"[0-9a-f]{12}", run_id):
        raise HTTPException(404, "Run tidak ditemukan.")
    root = runs_root()
    folder = (root / run_id).resolve()
    if not folder.is_relative_to(root) or not folder.is_dir():
        raise HTTPException(404, "Run tidak ditemukan.")
    return folder


async def save_upload(upload: UploadFile, path: Path) -> None:
    """Stream an upload to a canonical name; never trust the user's filename as a path."""
    limit = min(
        MAX_UPLOAD_BYTES, int(os.environ.get("BIOTRACE_MAX_UPLOAD_MB", "200")) * 1024 * 1024
    )
    size = 0
    with path.open("xb") as stream:
        while chunk := await upload.read(1024 * 1024):
            size += len(chunk)
            if size > limit:
                raise HTTPException(413, "Ukuran file melebihi batas unggah.")
            stream.write(chunk)


def get_result(run_id: str) -> RunResult:
    try:
        return read_run(run_folder(run_id))
    except FileNotFoundError as exc:
        raise HTTPException(404, "Run tidak ditemukan.") from exc


@app.get("/api/health", response_model=HealthResponse)
def health() -> dict:
    cfg = load_rules()
    ready = reference_root().joinpath("manifest.json").is_file()
    manifest = json.loads((reference_root() / "manifest.json").read_text()) if ready else {}
    return {
        "engine_version": __version__,
        "rules_version": cfg.rules_version,
        "rules_status": cfg.status,
        "reference_version": manifest.get("reference_version"),
        "reference_ready": manifest.get("counts", {}).get("species_with_reference", 0) > 0,
        "blast_available": bool(executable("blastn") and executable("makeblastdb")),
        "demo_available": DEMO.is_dir(),
    }


@app.post("/api/runs", response_model=RunCreated)
async def create_run(
    reads: Annotated[UploadFile, File()],
    metadata: Annotated[UploadFile, File()],
    fasta: Annotated[UploadFile | None, File()] = None,
    taxonomy: Annotated[UploadFile | None, File()] = None,
    site_context: Annotated[UploadFile | None, File()] = None,
    mode: Annotated[str, Form()] = "normal",
    waterbody_id: Annotated[str, Form()] = "",
    marker: Annotated[str, Form()] = "",
) -> RunCreated:
    if mode not in {"normal", "simulation"}:
        raise HTTPException(
            422,
            "Unggahan menerima mode normal atau simulation. Validasi luar dijalankan melalui CLI.",
        )
    with tempfile.TemporaryDirectory(prefix="biotrace-upload-") as temp:
        paths = {}
        for role, upload in {
            "reads": reads,
            "metadata": metadata,
            "fasta": fasta,
            "taxonomy": taxonomy,
            "site_context": site_context,
        }.items():
            paths[role] = None
            if upload is None:
                continue
            suffix = Path(upload.filename or "").suffix.lower()
            if suffix not in ALLOWED_EXTENSIONS:
                raise HTTPException(422, "Ekstensi unggahan tidak diizinkan.")
            if role == "fasta" and suffix not in {".fasta", ".fa", ".fna"}:
                raise HTTPException(422, "Peran FASTA memerlukan file .fasta/.fa/.fna.")
            if role != "fasta" and suffix not in {".csv", ".tsv"}:
                raise HTTPException(422, "Peran tabel memerlukan CSV/TSV.")
            simulated = mode == "simulation"
            if simulated and "SIMULASI" not in (upload.filename or ""):
                raise HTTPException(422, "Nama file simulasi wajib memuat SIMULASI.")
            path = Path(temp) / artifact_name(role, suffix.lstrip("."), simulated)
            await save_upload(upload, path)
            paths[role] = path
        ref = DEMO / "reference_SIMULASI" if mode == "simulation" else reference_root()
        result = await run_in_threadpool(
            run_analysis,
            paths["reads"],
            paths["metadata"],
            paths["fasta"],
            paths["taxonomy"],
            paths["site_context"],
            ref,
            DEFAULT_RULES,
            runs_root(),
            mode,
            4,
            defaults={"waterbody_id": waterbody_id.strip(), "marker": marker.strip()},
        )
    return RunCreated(
        run_id=result.run_id, validation=result.validation, is_simulated=result.summary.is_simulated
    )


INSPECT_BYTES = 256 * 1024


@app.post("/api/inputs/inspect", response_model=InspectResponse)
async def inspect_input(file: Annotated[UploadFile, File()]) -> dict:
    """D-039: recognise a file's role and columns from its first rows (nothing is stored)."""
    head = (await file.read(INSPECT_BYTES)).decode("utf-8-sig", errors="replace")
    waterbodies = {
        r["waterbody_id"]: r.get("name", "")
        for r in read_table(reference_root() / "waterbodies.csv")
    }
    options = [{"waterbody_id": k, "name": v} for k, v in sorted(waterbodies.items())]
    empty = {"columns": {}, "ignored": [], "notes": [], "needs": [], "waterbodies": options}
    if head.lstrip().startswith(">"):
        return {**empty, "role": "fasta"}
    lines = head.splitlines()
    if len(head) >= INSPECT_BYTES:
        lines = lines[:-1]
    if not lines:
        return {**empty, "role": "unknown"}
    tsv = (file.filename or "").lower().endswith(".tsv") or "\t" in lines[0]
    reader = csv.reader(lines, delimiter="\t" if tsv else ",")
    headers = [h.strip() for h in next(reader)]
    # Short rows are padded; cells beyond the header are dropped (inspection only).
    padded = [[c.strip() for c in cells] + [""] * len(headers) for cells in reader]
    rows = [
        dict(zip(headers, cells[: len(headers)], strict=True)) for cells in padded if any(cells)
    ]
    role = detect_role(headers, rows)
    if role not in ALIASES or not rows:
        return {**empty, "role": role}
    mapped, mapping = map_table(rows, role)
    notes, needs = mapping.changes(), []
    if role == "metadata" and "sample_id" in mapped[0]:
        prepared, extra = prepare_metadata(mapped, waterbodies, {})
        notes += extra
        if any(r["sample_type"] == "sampel" and not r["waterbody_id"] for r in prepared):
            needs.append("waterbody_id")
        if any(not r["marker"] for r in prepared):
            needs.append("marker")
    return {
        **empty,
        "role": role,
        "columns": mapping.columns,
        "ignored": mapping.ignored,
        "notes": notes,
        "needs": needs,
    }


def _from_precomputed(folder: Path) -> RunResult:
    if not verify_run(folder)["valid"]:
        raise HTTPException(
            503, "Integritas hasil pra-hitung tidak cocok; jalankan ulang analisis."
        )
    result = read_run(folder)
    root = runs_root()
    root.mkdir(parents=True, exist_ok=True)
    destination = root / result.run_id
    if not destination.exists():
        with tempfile.TemporaryDirectory(prefix=".demo-import-", dir=root) as temp:
            staging = Path(temp) / "run"
            shutil.copytree(folder, staging)
            if not verify_run(staging)["valid"]:
                raise HTTPException(503, "Salinan pra-hitung tidak lolos pemeriksaan integritas.")
            try:
                staging.rename(destination)
            except OSError:
                if not destination.exists():
                    raise
                # Another request may have atomically published the same complete run.
    if not verify_run(destination)["valid"]:
        raise HTTPException(409, "Salinan run lokal berubah; hasil asli tidak ditimpa.")
    return result


@app.post("/api/runs/demo/{demo_id}", response_model=RunCreated)
def create_demo_run(demo_id: str) -> RunCreated:
    if demo_id == REAL_DEMO_ID:
        # Analisis penuh butuh beberapa menit; hasil pra-hitung terverifikasi dipakai bila ada.
        precomputed = ROOT / "precomputed" / REAL_PRECOMPUTED_NAME
        if precomputed.exists() and verify_run(precomputed)["valid"]:
            result = _from_precomputed(precomputed)
            return RunCreated(
                run_id=result.run_id,
                validation=result.validation,
                is_simulated=False,
                precomputed=True,
            )
        if not executable("blastn"):
            raise HTTPException(503, "BLAST tidak tersedia dan hasil data asli belum dipra-hitung.")
        result = run_analysis(
            REAL_DEMO / "reads.csv",
            REAL_DEMO / "metadata.csv",
            REAL_DEMO / "asv.fasta",
            REAL_DEMO / "taxonomy.csv",
            None,
            REAL_REF,
            out_root=runs_root(),
            mode="normal",
            provenance=REAL_PROVENANCE,
        )
        return RunCreated(run_id=result.run_id, validation=result.validation, is_simulated=False)
    if demo_id != DEMO_ID:
        raise HTTPException(404, "Demo tidak ditemukan.")
    if not executable("blastn"):
        precomputed = ROOT / "precomputed" / PRECOMPUTED_NAME
        if not precomputed.exists() or not verify_run(precomputed)["valid"]:
            raise HTTPException(503, "BLAST tidak tersedia dan hasil demo pra-hitung belum siap.")
        result = _from_precomputed(precomputed)
        return RunCreated(
            run_id=result.run_id, validation=result.validation, is_simulated=True, precomputed=True
        )
    result = run_analysis(
        DEMO / "reads_SIMULASI.csv",
        DEMO / "metadata_SIMULASI.csv",
        DEMO / "asv_SIMULASI.fasta",
        DEMO / "taxonomy_SIMULASI.csv",
        None,
        DEMO / "reference_SIMULASI",
        out_root=runs_root(),
        mode="simulation",
    )
    return RunCreated(run_id=result.run_id, validation=result.validation, is_simulated=True)


@app.get("/api/runs/{run_id}", response_model=RunResult)
def result(run_id: str) -> RunResult:
    return get_result(run_id)


@app.get("/api/runs/{run_id}/claims", response_model=list[Claim])
def claims(
    run_id: str,
    decision: str | None = None,
    site_id: str | None = None,
    label: str | None = None,
    q: str = "",
    offset: int = Query(0, ge=0),
    limit: int = Query(1000, ge=1, le=10000),
) -> list[Claim]:
    rows = get_result(run_id).claims
    filtered = [
        c
        for c in rows
        if (not decision or c.decision == decision)
        and (not site_id or c.site_id == site_id)
        and (not label or label in c.labels)
        and (not q or q.casefold() in f"{c.reported_name} {c.taxon_lab} {c.asv_id}".casefold())
    ]
    return filtered[offset : offset + limit]


@app.get("/api/runs/{run_id}/claims/{claim_id}", response_model=Claim)
def claim(run_id: str, claim_id: str) -> Claim:
    for row in get_result(run_id).claims:
        if row.claim_id == claim_id:
            return row
    raise HTTPException(404, "Klaim tidak ditemukan.")


@app.get("/api/runs/{run_id}/coverage", response_model=list[CoverageRow])
def coverage_endpoint(run_id: str) -> list[CoverageRow]:
    return get_result(run_id).coverage


@app.get("/api/runs/{run_id}/barcode-priority", response_model=list[BarcodePriorityRow])
def priorities(run_id: str) -> list[BarcodePriorityRow]:
    return get_result(run_id).barcode_priority


@app.get("/api/runs/{run_id}/report.pdf")
def report(run_id: str) -> FileResponse:
    result = get_result(run_id)
    if not verify_run(run_folder(run_id))["valid"]:
        raise HTTPException(409, "Integritas run tidak cocok; laporan tidak diterbitkan.")
    name = artifact_name("report", "pdf", result.summary.is_simulated)
    return FileResponse(run_folder(run_id) / name, media_type="application/pdf", filename=name)


@app.get("/api/runs/{run_id}/summary.pdf")
def summary_report(run_id: str) -> StreamingResponse:
    """F24/D-038: bounded reading copy; complete canonical claims retain their fingerprint."""
    from biotrace_core.reference.store import manifest_path
    from biotrace_core.report.pdf import render_report

    result = get_result(run_id)
    if not verify_run(run_folder(run_id))["valid"]:
        raise HTTPException(409, "Integritas run tidak cocok; ringkasan tidak diterbitkan.")
    reference = (
        DEMO / "reference_SIMULASI"
        if result.summary.is_simulated
        else ROOT / "data/reference" / result.manifest.reference_version
    )
    if not reference.resolve().is_relative_to((ROOT / "data").resolve()):
        raise HTTPException(422, "Lokasi kamus tersimpan tidak sah.")
    mode = "simulation" if result.summary.is_simulated else "normal"
    ref = load_reference(reference, mode)
    if sha256(manifest_path(reference).read_bytes()) != result.manifest.reference_manifest_hash:
        raise HTTPException(409, "Kamus untuk laporan tersimpan tidak cocok.")
    with tempfile.TemporaryDirectory(prefix="biotrace-summary-") as temp:
        path = Path(temp) / "summary.pdf"
        render_report(result, ref.tables["sources"], path, brief=True)
        content = path.read_bytes()
    name = artifact_name("ringkasan", "pdf", result.summary.is_simulated)
    return StreamingResponse(
        io.BytesIO(content),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{name}"'},
    )


@app.get("/api/runs/{run_id}/export.zip")
def export(run_id: str) -> StreamingResponse:
    result = get_result(run_id)
    folder = run_folder(run_id)
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        for stem, ext in [
            ("claims", "csv"),
            ("coverage", "csv"),
            ("barcode_priority", "csv"),
            ("summary", "json"),
            ("run_manifest", "json"),
            ("validation_report", "json"),
        ]:
            name = artifact_name(stem, ext, result.summary.is_simulated)
            archive.write(folder / name, name)
    buffer.seek(0)
    name = artifact_name("biotrace_export", "zip", result.summary.is_simulated)
    return StreamingResponse(
        buffer,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{name}"'},
    )


@app.get("/api/reference", response_model=ReferenceStats)
def reference(simulation: bool = False) -> dict:
    cfg = load_rules()
    path = DEMO / "reference_SIMULASI" if simulation else reference_root()
    ref = load_reference(path, "simulation" if simulation else "normal")
    return reference_stats(
        ref.select(cfg, "simulation" if simulation else "normal", ref.manifest["marker"])
    )


@app.get("/api/reference/coverage", response_model=list[CoverageRow])
def reference_coverage(waterbody_id: str = "", simulation: bool = False) -> list[dict]:
    return [
        r
        for r in reference(simulation)["coverage"]
        if not waterbody_id or r["waterbody_id"] == waterbody_id
    ]


@app.get("/api/methods", response_model=MethodsResponse)
def methods() -> dict:
    return {
        "rules": load_rules().model_dump(mode="json"),
        "citations": [
            {
                "label": "Polanco dkk. 2025 - skor keyakinan",
                "url": "https://doi.org/10.1002/edn3.70077",
            },
            {"label": "Mai dkk. 2026 - PhyloRef", "url": "https://doi.org/10.1002/ece3.73159"},
            {"label": "Marques dkk. 2021 - GAPeDNA", "url": "https://doi.org/10.1111/ddi.13142"},
            {"label": "Zhu dkk. 2023 - MitoFish", "url": "https://doi.org/10.1093/molbev/msad035"},
            {
                "label": "Thalinger dkk. 2021 - skala validasi",
                "url": "https://doi.org/10.1002/edn3.189",
            },
        ],
    }


@app.get("/api/validation/latest", response_model=ValidationResults)
def latest_validation() -> dict:
    results = sorted((ROOT / "validation/results").glob("*.json"))
    return {
        "available": bool(results),
        "results": [json.loads(p.read_text(encoding="utf-8")) for p in results],
    }


@app.get("/api/datasets", response_model=DatasetsResponse)
def datasets() -> dict:
    path = ROOT / "data/external/lake_st_pierre/v20250924/dataset_manifest.json"
    return {
        "lake_st_pierre": json.loads(path.read_text(encoding="utf-8")) if path.is_file() else None,
        "guyana_available": (ROOT / "data/external/french_guiana_12s/v1/manifest.json").is_file(),
    }


@app.post("/api/verify", response_model=VerifyResponse)
def verify_report(body: VerifyRequest) -> dict:
    """F28 [P1]: report code (full or 12-character prefix) against runs on this machine."""
    if not re.fullmatch(r"[0-9a-fA-F]{12}([0-9a-fA-F]{52})?", body.report_fingerprint.strip()):
        raise HTTPException(422, "Kode verifikasi berisi 12 atau 64 karakter heksadesimal.")
    return find_by_fingerprint(runs_root(), body.report_fingerprint)


@app.get("/api/runs/{run_id}/notes", response_model=list[ReviewNote])
def notes(run_id: str) -> list[ReviewNote]:
    return load_notes(run_folder(run_id))


@app.post("/api/runs/{run_id}/claims/{claim_id}/notes", response_model=ReviewNote)
def create_note(run_id: str, claim_id: str, body: NoteRequest) -> ReviewNote:
    """F29 [P1]: append-only expert note; it never changes the claim or the fingerprint."""
    return add_note(run_folder(run_id), claim_id, body.reviewer, body.note, body.verified)


@app.get("/api/runs/{run_id}/sites", response_model=list[SitePoint])
def sites(run_id: str) -> list[SitePoint]:
    decimals = int(os.environ.get("BIOTRACE_MASK_DECIMALS", "1"))
    return site_points(run_folder(run_id), decimals)


@app.get("/api/runs/{run_id}/compare/{other_id}", response_model=RunComparison)
def compare(run_id: str, other_id: str) -> RunComparison:
    return compare_runs(get_result(run_id), get_result(other_id))


@app.post("/api/runs/{run_id}/rematch", response_model=RunComparison)
async def rematch_run(run_id: str) -> RunComparison:
    """F32 [P2]: rerun stored inputs against the ACTIVE reference and rules, then diff."""
    base = get_result(run_id)
    ref = DEMO / "reference_SIMULASI" if base.summary.is_simulated else reference_root()
    _, comparison = await run_in_threadpool(
        rematch, run_folder(run_id), ref, DEFAULT_RULES, runs_root()
    )
    return comparison


@app.post("/api/reference/proposals", response_model=ProposalResponse)
async def create_proposal(
    fasta: Annotated[UploadFile, File()],
    metadata: Annotated[UploadFile, File()],
    simulation: Annotated[bool, Form()] = False,
) -> dict:
    """F31 [P1]: automatic curation report for proposed sequences; nothing enters the reference."""
    if Path(fasta.filename or "").suffix.lower() not in {".fasta", ".fa", ".fna"}:
        raise HTTPException(422, "Usulan sekuens memerlukan file .fasta/.fa/.fna.")
    if Path(metadata.filename or "").suffix.lower() not in {".csv", ".tsv"}:
        raise HTTPException(422, "Metadata sekuens memerlukan CSV/TSV.")
    cfg = load_rules()
    mode = "simulation" if simulation else "normal"
    source = load_reference(DEMO / "reference_SIMULASI" if simulation else reference_root(), mode)
    source = source.select(cfg, mode, source.manifest["marker"])
    with tempfile.TemporaryDirectory(prefix="biotrace-proposal-") as temp:
        fasta_path = Path(temp) / "sequences.fasta"
        meta_path = Path(temp) / f"metadata{Path(metadata.filename or '').suffix.lower()}"
        await save_upload(fasta, fasta_path)
        await save_upload(metadata, meta_path)
        root = Path(os.environ.get("BIOTRACE_PROPOSALS_DIR", str(ROOT / "proposals"))).resolve()
        return await run_in_threadpool(propose_sequences, fasta_path, meta_path, source, cfg, root)


dist = ROOT / "web/dist"
if (dist / "assets").is_dir():
    app.mount("/assets", StaticFiles(directory=dist / "assets"), name="assets")


@app.get("/{path:path}", include_in_schema=False)
def frontend(path: str) -> FileResponse:
    if path.startswith("api/") or not (dist / "index.html").is_file():
        raise HTTPException(404, "Halaman tidak ditemukan atau frontend belum dibangun.")
    return FileResponse(dist / "index.html")
