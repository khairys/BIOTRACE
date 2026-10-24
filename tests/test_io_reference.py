"""V-01..10, R-NAME-01, R-CUR-* and R-COV-* boundaries [MVP]."""

import pytest

from biotrace_core.io.loaders import read_fasta, read_table, write_table
from biotrace_core.io.validate import InputError, load_inputs
from biotrace_core.reference.curate import curate_records, write_reference
from biotrace_core.reference.store import coverage, load_reference
from biotrace_core.reference.trim import reverse_complement, trim_mifish
from scripts.make_demo_data import create_demo


@pytest.fixture
def inputs(tmp_path):
    return create_demo(tmp_path / "SIMULASI")


def load(path, **changes):
    args = {
        "reads_path": path / "reads_SIMULASI.csv",
        "metadata_path": path / "metadata_SIMULASI.csv",
        "fasta_path": path / "asv_SIMULASI.fasta",
        "taxonomy_path": path / "taxonomy_SIMULASI.csv",
        "site_context_path": None,
        "waterbodies": {"MATANO"},
        "mode": "simulation",
    }
    args.update(changes)
    return load_inputs(**args)


def test_V_01_valid_and_duplicate_reads(inputs):
    assert len(load(inputs).samples) == 18
    path = inputs / "reads_SIMULASI.csv"
    rows = read_table(path)
    write_table(path, rows + [rows[0]])
    with pytest.raises(InputError, match="wajib unik"):
        load(inputs)


def test_R_PRE_01_wide_excludes_simulation_flag(inputs):
    path = inputs / "reads_SIMULASI.csv"
    write_table(path, [{"asv_id": "A", "MAT_S1_R1": 100, "MAT_S1_R2": 0, "is_simulated": True}])
    data = load(inputs)
    assert {r.sample_id for r in data.reads} == {"MAT_S1_R1", "MAT_S1_R2"}


def test_V_02_unknown_sample_warning(inputs):
    path = inputs / "reads_SIMULASI.csv"
    rows = read_table(path)
    rows[0]["sample_id"] = "not_in_metadata"
    write_table(path, rows)
    data = load(inputs)
    assert any(i.code == "V-02" and i.level == "warning" for i in data.report.issues)


@pytest.mark.parametrize(
    "field,value,code",
    [("waterbody_id", "UNKNOWN", "V-03"), ("latitude", "999", "V-06"), ("marker", "COI", "V-09")],
)
def test_V_03_06_09_metadata(inputs, field, value, code):
    path = inputs / "metadata_SIMULASI.csv"
    rows = read_table(path)
    rows[0][field] = value
    write_table(path, rows)
    if code == "V-06":
        assert any(i.code == code for i in load(inputs).report.issues)
    else:
        with pytest.raises(InputError) as error:
            load(inputs)
        assert any(i.code == code for i in error.value.report.issues)


def test_V_04_multiple_waterbodies(inputs):
    path = inputs / "metadata_SIMULASI.csv"
    rows = read_table(path)
    rows[0]["waterbody_id"] = "OTHER"
    write_table(path, rows)
    with pytest.raises(InputError) as exc:
        load(inputs, waterbodies={"MATANO", "OTHER"})
    assert any(i.code == "V-04" for i in exc.value.report.issues)


def test_V_05_no_negative_control(inputs):
    path = inputs / "metadata_SIMULASI.csv"
    rows = [r for r in read_table(path) if r["sample_type"] == "sampel"]
    write_table(path, rows)
    assert any(i.code == "V-05" for i in load(inputs).report.issues)


def test_V_07_missing_fasta_asv(inputs):
    path = inputs / "asv_SIMULASI.fasta"
    text = path.read_text()
    path.write_text("\n".join(text.splitlines()[2:]) + "\n")
    assert any(i.code == "V-07" for i in load(inputs).report.issues)


def test_V_08_no_naming_input(inputs):
    with pytest.raises(InputError) as exc:
        load(inputs, fasta_path=None, taxonomy_path=None)
    assert any(i.code == "V-08" for i in exc.value.report.issues)


def test_V_10_bad_extension(inputs):
    bad = inputs / "bad_SIMULASI.exe"
    bad.write_text("not executable")
    with pytest.raises(InputError) as exc:
        load(inputs, reads_path=bad)
    assert any(i.code == "V-10" for i in exc.value.report.issues)


def test_V_SIM_mixed_rows_rejected(inputs):
    path = inputs / "reads_SIMULASI.csv"
    rows = read_table(path)
    rows[0]["is_simulated"] = "false"
    write_table(path, rows)
    with pytest.raises(InputError, match="is_simulated"):
        load(inputs)


def test_V_01_negative_or_fractional_reads(inputs):
    path = inputs / "reads_SIMULASI.csv"
    rows = read_table(path)
    rows[0]["reads"] = "1.5"
    write_table(path, rows)
    with pytest.raises(InputError, match="integer"):
        load(inputs)


def test_R_NAME_01_external_rejected_before_open(tmp_path):
    with pytest.raises(ValueError, match="external"):
        load_reference(tmp_path / "data/external/evil", "normal")


def test_R_NAME_01_V4_simulation_marker_country_guards(ref, cfg):
    ref.sequences = [r.model_copy(update={"voucher_level": "V4"}) for r in ref.sequences]
    assert not ref.select(cfg, "simulation", "12S_MiFish_U").eligible
    with pytest.raises(ValueError, match="SIMULASI"):
        ref.select(cfg, "normal", "12S_MiFish_U")


def test_R_CUR_02_V4_never_imported(ref, cfg):
    row = ref.sequences[0].model_dump()
    row["voucher_level"] = "V4"
    records, _, report = curate_records([row], ref.fasta, ref, cfg, "12S_MiFish_U")
    assert records == []
    assert report[0]["reason"] == "environmental_sequence"


def test_R_CUR_05_both_orientations(cfg):
    forward = str(cfg.curation["forward_primer"])
    reverse = reverse_complement(str(cfg.curation["reverse_primer"]))
    insert = "ACGT" * 42 + "AC"
    sequence = forward + insert + reverse
    assert trim_mifish(sequence, cfg) == insert
    assert trim_mifish(reverse_complement(sequence), cfg) == insert
    assert trim_mifish("A" * 170, cfg) is None


def test_R_CUR_06_short_and_N_rejected(ref, cfg):
    first = ref.sequences[0].model_dump()
    second = ref.sequences[1].model_dump()
    first["seq_id"] = "N"
    second["seq_id"] = "SHORT"
    _, _, report = curate_records(
        [first, second], {"N": "N" * 170, "SHORT": "A" * 50}, ref, cfg, "12S_MiFish_U"
    )
    assert {r["reason"] for r in report} == {"short", "ambiguous"}


def test_R_CUR_07_08_duplicates_and_conflicts(ref, cfg):
    first = ref.sequences[0].model_dump()
    second = ref.sequences[1].model_dump()
    second["seq_id"] = "OTHER"
    second["species_original"] = first["species_original"]
    second["species_valid"] = first["species_valid"]
    records, _, report = curate_records(
        [first, second],
        {first["seq_id"]: "ACGT" * 42 + "AC", "OTHER": "ACGT" * 42 + "AC"},
        ref,
        cfg,
        "12S_MiFish_U",
    )
    assert len(records) == 1
    assert any(r["step"] == "R-CUR-07" for r in report)
    second["species_original"] = "Gobio epsilon"
    second["species_valid"] = "Gobio epsilon"
    records, _, _ = curate_records(
        [first, second],
        {first["seq_id"]: "ACGT" * 42 + "AC", "OTHER": "ACGT" * 42 + "AC"},
        ref,
        cfg,
        "12S_MiFish_U",
    )
    assert len(records) == 2
    assert all(r.curation_status == "accepted" and r.flags == "conflict" for r in records)


def test_R_CUR_10_no_license(ref, cfg):
    row = ref.sequences[0].model_dump()
    row["license"] = ""
    records, _, report = curate_records([row], ref.fasta, ref, cfg, "12S_MiFish_U")
    assert not records and report[0]["step"] == "R-CUR-10"


def test_R_CUR_11_immutable_and_hash_validation(inputs):
    ref_path = inputs / "reference_SIMULASI"
    before = (ref_path / "manifest_SIMULASI.json").read_bytes()
    with pytest.raises(FileExistsError):
        write_reference(ref_path, "new", "ID", "12S_MiFish_U", {}, {})
    assert (ref_path / "manifest_SIMULASI.json").read_bytes() == before
    (ref_path / "taxa_SIMULASI.csv").write_text("tampered")
    with pytest.raises(ValueError, match="Sidik jari"):
        load_reference(ref_path, "simulation")


def test_R_COV_01_checklist_denominators(ref):
    rows = {r.genus: r for r in coverage(ref)}
    assert (rows["Piscis"].n, rows["Piscis"].r) == (3, 2)
    assert (rows["Gobio"].n, rows["Gobio"].r) == (2, 2)
    assert rows["Rasbo"].p_missing == 0.5


def test_fasta_duplicate_and_invalid_bases(tmp_path):
    p = tmp_path / "SIMULASI.fasta"
    p.write_text(">A\nACGT\n>A\nACGT\n")
    with pytest.raises(ValueError, match="duplikat"):
        read_fasta(p)
