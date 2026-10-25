"""Cross-platform setup/test/demo commands [MVP]; stdlib launcher, Python 3.11 via uv."""

import argparse
import os
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run(*args: str) -> None:
    subprocess.run(list(args), cwd=ROOT, check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "task",
        choices=[
            "setup",
            "test",
            "test-slow",
            "build",
            "demo",
            "dev",
            "precompute",
            "schemas",
            "ref-build",
        ],
    )
    args = parser.parse_args()
    uv = shutil.which("uv") or "uv"
    npm = shutil.which("npm.cmd" if os.name == "nt" else "npm") or "npm"
    task = args.task
    if task == "setup":
        run(uv, "sync", "--frozen")
        run(npm, "ci", "--prefix", "web")
        if os.name == "nt":
            run(uv, "run", "python", "scripts/install_tools.py", "--blast")
        run(uv, "run", "python", "scripts/prepare_jury.py", "check")
        if not (ROOT / "data/demo/matano_SIMULASI_v3").exists():
            run(uv, "run", "python", "scripts/make_demo_data.py")
    elif task in {"test", "test-slow"}:
        run(uv, "run", "ruff", "format", "--check", "biotrace_core", "api", "scripts", "tests")
        run(uv, "run", "ruff", "check", "biotrace_core", "api", "scripts", "tests")
        run(uv, "run", "pytest", "-m", "slow" if task == "test-slow" else "not slow", "-q")
    elif task in {"build", "schemas"}:
        run(uv, "run", "python", "scripts/export_schemas.py")
        if task == "build":
            run(npm, "run", "build", "--prefix", "web")
    elif task == "precompute":
        run(uv, "run", "python", "scripts/precompute.py")
    elif task == "ref-build":
        run(
            uv,
            "run",
            "biotrace",
            "ref",
            "build",
            "--ref",
            "data/demo/matano_SIMULASI_v3/reference_SIMULASI",
            "--mode",
            "simulation",
        )
    else:
        if task == "demo":
            run(npm, "run", "build", "--prefix", "web")
        else:
            vite = subprocess.Popen([npm, "run", "dev", "--prefix", "web"], cwd=ROOT)
        try:
            run(
                uv,
                "run",
                "uvicorn",
                "api.main:app",
                "--host",
                "127.0.0.1",
                "--port",
                "8000",
                *(["--reload"] if task == "dev" else []),
            )
        finally:
            if task == "dev":
                vite.terminate()


if __name__ == "__main__":
    main()
