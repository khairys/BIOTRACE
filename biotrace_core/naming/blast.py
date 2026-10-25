"""R-NAME-02 [MVP] local BLAST+ subprocess adapter; never accesses a network."""

import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from biotrace_core.config import ROOT, RulesConfig, blast_timeout
from biotrace_core.io.loaders import write_fasta
from biotrace_core.models import SpeciesHit
from biotrace_core.reference.store import ReferenceIndex

OUTFMT = "6 qseqid sseqid pident length mismatch gapopen qstart qend sstart send evalue bitscore qlen slen qcovs"


def reference_seq_id(identifier: str, species_map: dict[str, str]) -> str:
    """Resolve NCBI's gb|accession| / lcl|id wrappers to an existing local ID only."""
    if identifier in species_map:
        return identifier
    matches = [part for part in identifier.split("|") if part in species_map]
    if len(matches) == 1:
        return matches[0]
    raise ValueError("BLAST mengembalikan ID di luar kamus aktif.")


def executable(name: str) -> str | None:
    directory = os.environ.get("BIOTRACE_BLAST_BIN")
    suffix = ".exe" if os.name == "nt" else ""
    if directory and (Path(directory) / f"{name}{suffix}").is_file():
        return str(Path(directory) / f"{name}{suffix}")
    found = shutil.which(name)
    if found:
        return found
    bundled = ROOT / ".tools/ncbi-blast-2.17.0+/bin" / f"{name}{suffix}"
    return str(bundled) if bundled.is_file() else None


def blast_version() -> str:
    path = executable("blastn")
    if not path:
        return "unavailable"
    return subprocess.run(
        [path, "-version"], check=True, capture_output=True, text=True
    ).stdout.splitlines()[0]


def build_database(ref: ReferenceIndex, folder: Path) -> Path:
    """R-NAME-01/02. Only eligible references enter the local BLAST database."""
    tool = executable("makeblastdb")
    if not tool:
        raise ValueError(
            "NCBI BLAST+ belum tersedia. Pasang makeblastdb/blastn atau gunakan taksonomi lab."
        )
    folder.mkdir(parents=True, exist_ok=True)
    # NCBI's Windows DB self-check splits absolute paths containing spaces.
    # Build in a local temporary working directory and preserve the resulting DB.
    if os.name == "nt" and " " in str(folder.resolve()):
        with tempfile.TemporaryDirectory(prefix="biotrace-blast-") as work:
            build_database(ref, Path(work))
            for path in Path(work).iterdir():
                shutil.copyfile(path, folder / path.name)
        return folder / "ref"
    fasta = folder / "blast_input.fasta"
    write_fasta(fasta, {r.seq_id: ref.fasta[r.seq_id] for r in ref.eligible})
    prefix = folder / "ref"
    if ref.eligible:
        try:
            subprocess.run(
                [tool, "-in", fasta.name, "-dbtype", "nucl", "-out", prefix.name, "-parse_seqids"],
                cwd=folder.resolve(),
                check=True,
                capture_output=True,
                text=True,
                timeout=blast_timeout(),
            )
        except subprocess.TimeoutExpired as exc:
            raise ValueError(
                "Pembuatan database BLAST melewati anggaran eksekusi. "
                "Periksa proses lokal lalu ulangi; hasil parsial tidak diterbitkan."
            ) from exc
        except subprocess.CalledProcessError as exc:
            raise ValueError("Pembuatan database BLAST gagal; periksa instalasi lokal.") from exc
    return prefix


def match_sequences(
    query: dict[str, str], ref: ReferenceIndex, cfg: RulesConfig, folder: Path, threads: int = 4
) -> tuple[dict[str, list[SpeciesHit]], str]:
    """R-NAME-02. Stable ordering despite BLAST thread scheduling and HSP ties."""
    if not ref.eligible:
        return {}, ""
    if os.name == "nt" and " " in str(folder.resolve()):
        with tempfile.TemporaryDirectory(prefix="biotrace-blast-") as work:
            result = match_sequences(query, ref, cfg, Path(work), threads)
            folder.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(Path(work) / "blast_input.fasta", folder / "blast_input.fasta")
            return result
    tool = executable("blastn")
    if not tool:
        raise ValueError("NCBI BLAST+ belum tersedia untuk analisis FASTA unggahan.")
    prefix = build_database(ref, folder)
    query_path = folder / "query.fasta"
    write_fasta(query_path, query)
    args = [
        tool,
        "-query",
        query_path.name,
        "-db",
        prefix.name,
        "-num_threads",
        str(threads),
        "-outfmt",
        OUTFMT,
    ]
    for key, value in cfg.blast.items():
        args.extend([f"-{key}", str(value)])
    timeout = blast_timeout()
    try:
        completed = subprocess.run(
            args, cwd=folder.resolve(), check=True, capture_output=True, text=True, timeout=timeout
        )
    except subprocess.TimeoutExpired as exc:
        raise ValueError(
            f"Pencocokan {len(query)} ASV belum selesai dalam {timeout} detik. "
            "Hasil parsial tidak diterbitkan. Atur BIOTRACE_BLAST_TIMEOUT_SECONDS "
            "(maksimal 3600) lalu ulangi analisis; ambang biologis tetap sama."
        ) from exc
    except subprocess.CalledProcessError as exc:
        raise ValueError(
            "BLAST gagal memproses data lokal; periksa instalasi dan berkas input."
        ) from exc
    rows = [line.split("\t") for line in completed.stdout.splitlines() if line.strip()]
    rows.sort(key=lambda r: (r[0], -float(r[2]), -float(r[11]), r[1], int(r[6]), int(r[7])))
    seq_map = {r.seq_id: r.species_valid for r in ref.eligible}
    hits: dict[str, list[SpeciesHit]] = {}
    filtered = []
    for row in rows:
        cov = float(row[14]) / 100
        if cov >= cfg.naming.min_query_coverage:
            seq_id = reference_seq_id(row[1], seq_map)
            hits.setdefault(row[0], []).append(
                SpeciesHit(
                    species=seq_map[seq_id],
                    pct=float(row[2]),
                    bitscore=float(row[11]),
                    seq_id=seq_id,
                    query_coverage=cov,
                )
            )
            filtered.append("\t".join(row))
    return hits, "\n".join(filtered) + ("\n" if filtered else "")
