"""FastAPI local adapter [MVP]; same-origin static React and bounded file input."""

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
    MethodsResponse,
    ReferenceStats,
    ValidationResults,
)
from biotrace_core import __version__
from biotrace_core.audit import read_run, verify_run
from biotrace_core.config import DEFAULT_RULES, ROOT, load_rules
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


def runs_root() -> Path:
    return Path(os.environ.get("BIOTRACE_RUNS_DIR", str(ROOT / "runs"))).resolve()


def reference_root() -> Path:
    return Path(os.environ.get("BIOTRACE_REF_DIR", str(ROOT / "data/reference/v0.1"))).resolve()


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
            size = 0
            with path.open("xb") as stream:
                while chunk := await upload.read(1024 * 1024):
                    size += len(chunk)
                    if size > min(
                        MAX_UPLOAD_BYTES,
                        int(os.environ.get("BIOTRACE_MAX_UPLOAD_MB", "200")) * 1024 * 1024,
                    ):
                        raise HTTPException(413, "Ukuran file melebihi batas unggah.")
                    stream.write(chunk)
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
        )
    return RunCreated(
        run_id=result.run_id, validation=result.validation, is_simulated=result.summary.is_simulated
    )


@app.post("/api/runs/demo/{demo_id}", response_model=RunCreated)
def create_demo_run(demo_id: str) -> RunCreated:
    if demo_id != DEMO_ID:
        raise HTTPException(404, "Demo tidak ditemukan.")
    if not executable("blastn"):
        precomputed = ROOT / "precomputed/matano_SIMULASI_v3"
        if not precomputed.exists() or not verify_run(precomputed)["valid"]:
            raise HTTPException(503, "BLAST tidak tersedia dan hasil demo pra-hitung belum siap.")
        result = read_run(precomputed)
        root = runs_root()
        root.mkdir(parents=True, exist_ok=True)
        destination = root / result.run_id
        if not destination.exists():
            shutil.copytree(precomputed, destination)
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
    name = artifact_name("report", "pdf", result.summary.is_simulated)
    return FileResponse(run_folder(run_id) / name, media_type="application/pdf", filename=name)


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


dist = ROOT / "web/dist"
if (dist / "assets").is_dir():
    app.mount("/assets", StaticFiles(directory=dist / "assets"), name="assets")


@app.get("/{path:path}", include_in_schema=False)
def frontend(path: str) -> FileResponse:
    if path.startswith("api/") or not (dist / "index.html").is_file():
        raise HTTPException(404, "Halaman tidak ditemukan atau frontend belum dibangun.")
    return FileResponse(dist / "index.html")
