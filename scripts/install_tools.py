"""Install pinned local BLAST+ binaries; separate from data and analysis [MVP]."""

import argparse
import hashlib
import os
import tarfile
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def install_blast() -> Path:
    if os.name != "nt":
        raise ValueError("Pasang NCBI BLAST+ melalui pengelola paket OS; lihat README.")
    tools = ROOT / ".tools"
    tools.mkdir(exist_ok=True)
    destination = tools / "ncbi-blast-2.17.0+/bin/blastn.exe"
    if destination.exists():
        return destination.parent
    archive = tools / "ncbi-blast-2.17.0+-x64-win64.tar.gz"
    url = "https://ftp.ncbi.nlm.nih.gov/blast/executables/blast+/2.17.0/" + archive.name
    expected = urllib.request.urlopen(url + ".md5", timeout=60).read().decode("ascii").split()[0]
    if not archive.exists():
        partial = archive.with_suffix(archive.suffix + ".partial")
        urllib.request.urlretrieve(url, partial)
        partial.rename(archive)
    md5 = hashlib.md5()
    with archive.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            md5.update(block)
    if md5.hexdigest() != expected:
        raise ValueError("Checksum BLAST tidak cocok; arsip tidak diekstrak.")
    root = tools.resolve()
    with tarfile.open(archive) as package:
        if any(
            not (root / m.name).resolve().is_relative_to(root) or m.issym() or m.islnk()
            for m in package.getmembers()
        ):
            raise ValueError("Path arsip instalasi tidak aman.")
        package.extractall(root, filter="data")
    return destination.parent


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--blast", action="store_true", required=True)
    parser.parse_args()
    print(install_blast())
