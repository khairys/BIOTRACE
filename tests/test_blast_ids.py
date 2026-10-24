"""Regression: NCBI formats bare accessions as gb|accession| [R-NAME-02]."""

import pytest

from biotrace_core.naming.blast import reference_seq_id


def test_R_NAME_02_ncbi_wrapped_local_ids():
    names = {"ID_SIMULASI": "Fictisim alpha"}
    assert reference_seq_id("ID_SIMULASI", names) == "ID_SIMULASI"
    assert reference_seq_id("gb|ID_SIMULASI|", names) == "ID_SIMULASI"
    assert reference_seq_id("lcl|ID_SIMULASI", names) == "ID_SIMULASI"
    with pytest.raises(ValueError, match="di luar kamus"):
        reference_seq_id("gb|UNKNOWN_SIMULASI|", names)
