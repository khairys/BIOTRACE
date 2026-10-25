"""UI-01..08 [MVP] browser workflow against a running local server."""

import json
import os
from pathlib import Path
from urllib.parse import urlparse

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[1]
BASE = os.environ.get("BIOTRACE_TEST_URL", "http://127.0.0.1:8000")


def main() -> None:
    output = ROOT / "output/browser"
    output.mkdir(parents=True, exist_ok=True)
    errors = []
    external = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1440, "height": 1000}, device_scale_factor=1, accept_downloads=True
        )
        page = context.new_page()
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.on(
            "request",
            lambda request: (
                external.append(request.url)
                if urlparse(request.url).hostname not in {"127.0.0.1", "localhost", None}
                else None
            ),
        )
        page.goto(BASE)
        page.wait_for_load_state("networkidle")
        print("Initial headings:", page.locator("h1,h2").all_text_contents())
        print("Initial buttons:", page.get_by_role("button").all_text_contents())
        expect(page.get_by_role("heading", name="Periksa data eDNA Anda.")).to_be_visible()
        expect(page.get_by_role("button", name="Jalankan analisis")).to_be_disabled()
        page.screenshot(path=str(output / "01-upload.png"), full_page=True)
        page.get_by_role("button", name="Muat data demo (SIMULASI)").click()
        page.wait_for_url("**/runs/**", timeout=60000)
        page.wait_for_load_state("networkidle")
        expect(page.get_by_role("heading", name="Hasil verifikasi eDNA")).to_be_visible()
        expect(page.locator(".simulation-banner")).to_be_visible()
        expect(page.locator(".decision-tile")).to_have_count(4)
        page.screenshot(path=str(output / "02-results.png"), full_page=True)
        assert page.evaluate("document.documentElement.scrollWidth<=window.innerWidth")
        page.locator(".decision-tile.must_verify").click()
        page.locator(".claims-table tbody tr").first.click()
        expect(page.get_by_role("dialog")).to_be_visible()
        expect(
            page.get_by_role("dialog")
            .get_by_text("Deteksi DNA bukan bukti pasti ikan hidup di lokasi.", exact=True)
            .last
        ).to_be_visible()
        page.get_by_role("button", name="English", exact=True).click()
        expect(
            page.get_by_text(
                "DNA detection is not proof that the fish lives at the site.", exact=True
            )
        ).to_be_visible()
        page.screenshot(path=str(output / "03-evidence.png"))
        page.keyboard.press("Escape")
        expect(page.get_by_role("dialog")).to_have_count(0)
        page.get_by_label("Cari klaim").fill("NO_MATCH_SIMULASI")
        expect(page.get_by_text("Tidak ada klaim yang cocok dengan filter.")).to_be_visible()
        page.get_by_label("Cari klaim").fill("")
        page.get_by_label("Filter keputusan").select_option("")
        with page.expect_download() as download:
            page.get_by_role("link", name="Unduh PDF").click()
        pdf = download.value
        assert "SIMULASI" in pdf.suggested_filename
        pdf.save_as(str(output / "report_SIMULASI.pdf"))
        assert (output / "report_SIMULASI.pdf").read_bytes().startswith(b"%PDF")
        with page.expect_download() as download:
            page.get_by_role("link", name="Unduh CSV").click()
        download.value.save_as(str(output / "export_SIMULASI.zip"))
        page.set_viewport_size({"width": 1280, "height": 900})
        page.screenshot(path=str(output / "04-results-1280.png"), full_page=True)
        assert page.evaluate("document.documentElement.scrollWidth<=window.innerWidth")
        page.get_by_role("link", name="Metode & aturan").click()
        expect(page.get_by_role("heading", name="Parameter aktif")).to_be_visible()
        page.get_by_role("link", name="Validasi & dataset").click()
        page.wait_for_load_state("networkidle")
        expect(page.get_by_role("heading", name="Lake St. Pierre", exact=True)).to_be_visible()
        page.screenshot(path=str(output / "05-validation.png"), full_page=True)
        page.get_by_role("link", name="Analisis baru", exact=True).first.click()
        demo = ROOT / "data/demo/matano_SIMULASI_v3"
        page.locator("input[type=file]").set_input_files(
            [
                str(demo / name)
                for name in ["reads_SIMULASI.csv", "metadata_SIMULASI.csv", "asv_SIMULASI.fasta"]
            ]
        )
        expect(page.get_by_role("button", name="Jalankan analisis")).to_be_enabled()
        expect(page.get_by_label("Peran reads_SIMULASI.csv")).to_have_value("reads")
        expect(page.get_by_label("Peran metadata_SIMULASI.csv")).to_have_value("metadata")
        expect(page.get_by_label("Peran asv_SIMULASI.fasta")).to_have_value("fasta")
        page.get_by_role("button", name="Jalankan analisis").click()
        page.wait_for_url("**/runs/**", timeout=60000)
        expect(page.get_by_role("heading", name="Hasil verifikasi eDNA")).to_be_visible()
        page.goto(BASE)
        page.get_by_role("button", name="Muat data eDNA asli Indonesia", exact=True).click()
        page.wait_for_url("**/runs/**", timeout=60000)
        page.wait_for_load_state("networkidle")
        expect(page.locator(".real-data-banner")).to_be_visible()
        expect(page.locator(".simulation-banner")).to_have_count(0)
        real_url = page.url.split("?")[0]
        page.goto(real_url)  # Provenance must survive a shared URL without query-string labels.
        expect(page.locator(".real-data-banner")).to_contain_text("v0.5")
        run_id = real_url.rsplit("/", 1)[-1]
        real_run = page.request.get(f"{BASE}/api/runs/{run_id}").json()
        assert real_run["summary"]["total_claims"] == 4354
        assert real_run["manifest"]["reference_version"] == "v0.5"
        assert (
            real_run["manifest"]["parameters"]["data_provenance"]["dataset_id"]
            == "marwayana2022_mifishu"
        )
        page.screenshot(path=str(output / "06-real-data.png"))
        with page.expect_download() as download:
            page.get_by_role("link", name="Ringkasan PDF", exact=True).click()
        download.value.save_as(str(output / "ringkasan_asli.pdf"))
        assert (output / "ringkasan_asli.pdf").read_bytes().startswith(b"%PDF")
        page.set_viewport_size({"width": 390, "height": 844})
        assert page.evaluate("document.documentElement.scrollWidth<=window.innerWidth")
        page.screenshot(path=str(output / "07-real-data-mobile.png"))
        verification = page.request.post(
            f"{BASE}/api/verify",
            data={"report_fingerprint": real_run["manifest"]["report_fingerprint"]},
        ).json()
        assert verification["found"] and verification["valid"]
        assert not errors, errors
        assert not external, external
        result = {
            "workflow": "passed",
            "console_errors": errors,
            "external_requests": external,
            "viewports": [1440, 1280, 390],
            "upload_files": 3,
            "pdf_download": True,
            "zip_download": True,
            "real_demo_claims": 4354,
            "real_reference": "v0.5",
            "provenance_survives_reload": True,
            "report_verification": True,
            "brief_pdf_download": True,
        }
        (output / "browser_results.json").write_text(
            json.dumps(result, indent=2) + "\n", encoding="utf-8"
        )
        print(json.dumps(result))
        browser.close()


if __name__ == "__main__":
    main()
