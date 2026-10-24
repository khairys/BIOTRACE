"""F24 [MVP] A4 report, source attribution and explicit interpretation limits."""

from functools import partial
from pathlib import Path
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from biotrace_core.config import load_rules
from biotrace_core.decision import DECISIONS
from biotrace_core.models import RunResult

TEAL = colors.HexColor("#0F766E")
INK = colors.HexColor("#14212B")
MUTED = colors.HexColor("#5B6B78")
PAPER = colors.HexColor("#F1F6F6")
RANKS = {
    "species": "Spesies",
    "complex": "Kompleks",
    "genus": "Genus",
    "family": "Famili",
    "order": "Ordo",
    "unknown": "Tidak dikenal",
    "hybrid_alias": "Alias hibrida",
}
CAUSES = {"reference": "referensi", "marker": "marker", "sample": "sampel", "location": "lokasi"}
LABELS = {
    "endemic": "endemik",
    "threatened": "terancam",
    "invasive": "invasif",
    "hybrid_alias": "alias hibrida",
    "possible_unreferenced_endemic": "kemungkinan endemik tanpa referensi",
}


def render_report(result: RunResult, sources: list[dict], destination: Path) -> None:
    """A10/A11/A2. Escape all uploaded text; no external assets or network."""
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="BodyID",
            fontName="Helvetica",
            fontSize=8,
            leading=12,
            textColor=INK,
            spaceAfter=6,
            wordWrap="CJK",
        )
    )
    styles.add(
        ParagraphStyle(
            name="SmallID", parent=styles["BodyID"], fontSize=6.8, leading=9, spaceAfter=3
        )
    )
    styles.add(
        ParagraphStyle(
            name="TitleID",
            fontName="Helvetica-Bold",
            fontSize=24,
            leading=29,
            textColor=TEAL,
            spaceAfter=12,
        )
    )
    styles.add(
        ParagraphStyle(
            name="HeadingID",
            fontName="Helvetica-Bold",
            fontSize=13,
            leading=17,
            textColor=TEAL,
            spaceBefore=12,
            spaceAfter=8,
        )
    )
    styles.add(
        ParagraphStyle(
            name="KPI",
            parent=styles["BodyID"],
            fontSize=21,
            leading=26,
            alignment=TA_CENTER,
            textColor=TEAL,
        )
    )

    def para(text: object, style: str = "BodyID", italic: bool = False) -> Paragraph:
        safe = escape(str(text))
        return Paragraph(f"<i>{safe}</i>" if italic else safe, styles[style])

    def table(
        headers: list[str], rows: list[list], widths: list[float], compact: bool = False
    ) -> Table:
        cells = [[para(c, "SmallID") for c in headers]] + [
            [c if isinstance(c, Paragraph) else para(c, "SmallID") for c in row] for row in rows
        ]
        value = Table(cells, colWidths=widths, repeatRows=1, hAlign="LEFT")
        value.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), PAPER),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LINEBELOW", (0, 0), (-1, 0), 0.6, TEAL),
                    ("LINEBELOW", (0, 1), (-1, -1), 0.3, colors.HexColor("#E3E8EC")),
                    ("LEFTPADDING", (0, 0), (-1, -1), 7),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                    ("TOPPADDING", (0, 0), (-1, -1), 3 if compact else 7),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 3 if compact else 6),
                ]
            )
        )
        return value

    def decorate(page: canvas.Canvas, document: SimpleDocTemplate) -> None:
        page.saveState()
        if result.summary.is_simulated:
            page.setFillColor(colors.HexColor("#EEEEEE"))
            page.translate(A4[0] / 2, A4[1] / 2)
            page.rotate(45)
            page.setFont("Helvetica-Bold", 78)
            page.drawCentredString(0, 0, "SIMULASI")
            page.restoreState()
            page.saveState()
        page.setFillColor(MUTED)
        page.setFont("Helvetica", 7)
        page.drawString(
            18 * mm, A4[1] - 12 * mm, "BioTrace Indonesia | Laporan verifikasi pendukung data eDNA"
        )
        page.drawString(
            18 * mm,
            12 * mm,
            f"{result.manifest.report_fingerprint[:12]} | Bukan dokumen AMDAL resmi",
        )
        page.drawRightString(A4[0] - 18 * mm, 12 * mm, str(document.page))
        page.setFont("Helvetica", 6.5)
        page.drawString(18 * mm, 8 * mm, "Deteksi DNA bukan bukti pasti ikan hidup di lokasi.")
        page.restoreState()

    doc = SimpleDocTemplate(
        str(destination),
        pagesize=A4,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        topMargin=22 * mm,
        bottomMargin=20 * mm,
        title="Laporan verifikasi pendukung data eDNA",
        author="BioTrace Indonesia",
    )
    story = []
    if result.summary.is_simulated:
        story.extend(
            [
                para("SIMULASI - seluruh data demo dibuat untuk pengujian perangkat lunak."),
                Spacer(1, 4 * mm),
            ]
        )
    story.extend(
        [
            para("Laporan verifikasi\npendukung data eDNA", "TitleID"),
            para("Ringkasan eksekutif", "HeadingID"),
            para(
                f"Perairan: {', '.join(result.summary.waterbodies)} | Lokasi: {len(result.summary.sites)} | Run: {result.run_id}"
            ),
        ]
    )
    s = result.summary
    kpis = [
        [
            para(str(s.total_claims), "KPI"),
            para(str(s.total_taxa), "KPI"),
            para(f"{s.safe_percent:.0f}%", "KPI"),
            para(str(s.must_verify_count), "KPI"),
        ],
        [
            para("klaim", "SmallID"),
            para("taksa unik", "SmallID"),
            para("klaim aman", "SmallID"),
            para("wajib verifikasi", "SmallID"),
        ],
    ]
    kpis[0].append(
        para(f"{s.reference_coverage:.0%}" if s.reference_coverage is not None else "-", "KPI")
    )
    kpis[1].append(para("cakupan kamus", "SmallID"))
    kpi = Table(kpis, colWidths=[34.8 * mm] * 5)
    kpi.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), PAPER),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story.extend(
        [
            Spacer(1, 4 * mm),
            kpi,
            Spacer(1, 6 * mm),
            table(
                ["Keputusan", "Klaim / taksa", "Tindak lanjut"],
                [[d.label, f"{d.claims} / {d.taxa}", d.follow_up] for d in s.decisions],
                [37 * mm, 22 * mm, 115 * mm],
            ),
        ]
    )
    attention = sorted(
        [c for c in result.claims if c.decision in {"must_verify", "do_not_use"}],
        key=lambda c: (
            "endemic" not in c.labels,
            "invasive" not in c.labels,
            not c.in_negative_control,
            c.claim_id,
        ),
    )[:5]
    story.append(para("Perhatian utama", "HeadingID"))
    story.extend(
        para(f"{c.site_id} - {c.reported_name}: {DECISIONS[c.decision][0]} ({c.grade}).")
        for c in attention
    )
    if not attention:
        story.append(para("Tidak ada klaim wajib verifikasi atau jangan dipakai pada run ini."))
    story.extend(
        [
            para("Sidik jari laporan", "HeadingID"),
            para(result.manifest.report_fingerprint, "SmallID"),
            para(
                "Deteksi DNA bukan bukti pasti ikan hidup di lokasi. Laporan ini merupakan verifikasi pendukung, bukan dokumen AMDAL resmi."
            ),
            PageBreak(),
            para("Daftar klaim", "HeadingID"),
        ]
    )
    order = {"must_verify": 0, "do_not_use": 1, "with_note": 2, "safe": 3}
    ordered = sorted(result.claims, key=lambda c: (order[c.decision], c.site_id, c.asv_id))
    story.append(
        table(
            ["Lokasi / ASV", "Nama lab", "Nama aman", "Tingkat", "Nilai", "Keputusan", "Penyebab"],
            [
                [
                    f"{c.site_id}\n{c.asv_id}",
                    para(c.taxon_lab or "-", "SmallID", True),
                    para(c.reported_name, "SmallID", True),
                    RANKS[c.reported_rank],
                    c.grade,
                    DECISIONS[c.decision][0],
                    ", ".join(CAUSES.get(x, x) for x in c.causes) or "-",
                ]
                for c in ordered
            ],
            [22 * mm, 29 * mm, 32 * mm, 17 * mm, 10 * mm, 29 * mm, 35 * mm],
        )
    )
    story.extend([PageBreak(), para("Lampiran A - Evidence Card", "HeadingID")])
    selected = [c for c in ordered if c.decision in {"must_verify", "do_not_use"}]
    if not selected:
        story.append(para("Tidak ada kartu wajib verifikasi/jangan dipakai."))
    for i, c in enumerate(selected):
        block = [
            para(c.reported_name, "HeadingID", True),
            para(
                f"{c.site_id} | {c.asv_id} | {RANKS[c.reported_rank]} | Nilai {c.grade} | {DECISIONS[c.decision][0]}"
            ),
            para(
                f"Nama lab: {c.taxon_lab or '-'} | L1 {c.l1}/2, L2 {c.l2}/1, L4 {c.l4}/2 | {c.total_reads} bacaan."
            ),
            para("Penyebab: " + (", ".join(CAUSES.get(x, x) for x in c.causes) or "tidak ada")),
            para("Label: " + (", ".join(LABELS.get(x, x) for x in c.labels) or "tidak ada")),
        ]
        block.extend(
            para(reason, "SmallID") for reason in c.reasons_id if reason != c.interpretation_limit
        )
        block.extend(
            [
                para(
                    f"Voucher pendukung: {c.voucher_support or 'tidak tersedia'} | Aksesi: {', '.join(c.supporting_accessions) or '-'}",
                    "SmallID",
                ),
                para(c.origin_status, "SmallID"),
                para(c.origin_pathway, "SmallID"),
                para(c.origin_other_sources, "SmallID"),
                para(c.follow_up),
                para(c.interpretation_limit, "SmallID"),
                Spacer(1, 3 * mm),
            ]
        )
        story.append(KeepTogether(block))
        if i % 2 == 1 and i < len(selected) - 1:
            story.append(PageBreak())
    story.extend(
        [
            PageBreak(),
            para("Lampiran B - Kamus dan celah", "HeadingID"),
            table(
                ["Perairan", "Genus", "Punya referensi / tercatat", "Fraksi celah"],
                [
                    [r.waterbody_id, r.genus, f"{r.r} / {r.n}", f"{r.p_missing:.0%}"]
                    for r in result.coverage
                ],
                [30 * mm, 50 * mm, 60 * mm, 34 * mm],
            ),
            para("Prioritas barcode", "HeadingID"),
            table(
                ["Nama / ASV", "Skor", "Alasan"],
                [
                    [r.name_or_asv, r.score, ", ".join(r.reasons)]
                    for r in result.barcode_priority[:20]
                ],
                [75 * mm, 15 * mm, 84 * mm],
            ),
            PageBreak(),
            para("Lampiran C - Metode dan parameter", "HeadingID"),
            para(
                f"Aturan {result.manifest.rules_version}: usulan tim, belum dikalibrasi ahli. Mesin deterministik berbasis aturan, tanpa machine learning. Fraksi celah kamus bukan probabilitas keberadaan ikan."
            ),
            para("Mode: " + result.manifest.mode),
        ]
    )
    config = result.manifest.parameters.get("rules", load_rules().model_dump(mode="json"))
    params = [
        [f"{section}.{key}", value]
        for section in ("naming", "scoring", "preprocess", "curation", "priorities")
        for key, value in config.get(section, {}).items()
    ]
    story.append(table(["Parameter", "Nilai"], params, [110 * mm, 64 * mm], compact=True))
    story.extend([para("Sitasi metode", "HeadingID")])
    for source in [
        "Polanco dkk. 2025 - https://doi.org/10.1002/edn3.70077",
        "Mai dkk. 2026 (PhyloRef) - https://doi.org/10.1002/ece3.73159",
        "Marques dkk. 2021 (GAPeDNA) - https://doi.org/10.1111/ddi.13142",
        "Zhu dkk. 2023 (MitoFish) - https://doi.org/10.1093/molbev/msad035",
        "Thalinger dkk. 2021 - https://doi.org/10.1002/edn3.189",
    ]:
        story.append(para(source, "SmallID"))
    story.extend(
        [
            PageBreak(),
            para("Lampiran D - Jejak audit", "HeadingID"),
            para(
                f"Engine {result.manifest.engine_version}; kamus {result.manifest.reference_version}; aturan {result.manifest.rules_version}; BLAST {result.manifest.blast_version}."
            ),
            para("Sidik jari run: " + result.manifest.run_fingerprint, "SmallID"),
            para("Sidik jari laporan: " + result.manifest.report_fingerprint, "SmallID"),
        ]
    )
    for name, digest in sorted(result.manifest.input_hashes.items()):
        story.extend([para(name), para(digest, "SmallID")])
    story.append(para("Sumber dan lisensi kamus", "HeadingID"))
    for source in sources:
        story.append(
            para(
                f"{source.get('citation', '')} | {source.get('doi_or_url', '')} | Lisensi: {source.get('license', '')}",
                "SmallID",
            )
        )
    story.append(para("Batas interpretasi", "HeadingID"))
    story.append(
        para(
            "Deteksi DNA bukan bukti pasti ikan hidup di lokasi. Nilai A bukan kepastian. Laporan ini adalah verifikasi pendukung, bukan dokumen AMDAL resmi."
        )
    )
    doc.build(
        story,
        onFirstPage=decorate,
        onLaterPages=decorate,
        canvasmaker=partial(canvas.Canvas, invariant=1),
    )
