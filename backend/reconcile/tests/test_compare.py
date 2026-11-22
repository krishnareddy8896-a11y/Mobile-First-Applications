from decimal import Decimal

from reconcile.cleaning import normalize_ref, parse_amount
from reconcile.compare import compare


def entry(entry_id="E1", ref="REC-1", value=Decimal("100"), location="L1", date="2026-03-01"):
    return {"entry_id": entry_id, "ref": ref, "value": value, "location": location, "date": date}


def record(total=Decimal("100"), location="L1", date="2026-03-01", state="CONFIRMED"):
    return {"total": total, "location": location, "date": date, "state": state}


def reasons(rows):
    return [row["reason"] for row in rows]


def test_missing_in_b():
    rows = compare({"REC-1": record()}, [])
    assert "MISSING_IN_B" in reasons(rows)


def test_orphan_in_b():
    rows = compare({}, [entry(ref="REC-404")])
    assert "ORPHAN_IN_B" in reasons(rows)


def test_duplicate_in_b():
    rows = compare(
        {"REC-1": record(total=Decimal("100"))},
        [entry("E1", value=Decimal("50")), entry("E2", value=Decimal("25"))],
    )
    assert "DUPLICATE_IN_B" in reasons(rows)


def test_value_mismatch():
    rows = compare({"REC-1": record(total=Decimal("100"))}, [entry(value=Decimal("90"))])
    assert "VALUE_MISMATCH" in reasons(rows)


def test_blank_value_is_unknown_not_zero():
    assert parse_amount("") is None
    rows = compare({"REC-1": record()}, [entry(value=None)])
    assert "VALUE_MISMATCH" in reasons(rows)


def test_split_entries_sum_to_total():
    rows = compare(
        {"REC-1": record(total=Decimal("100"))},
        [entry("E1", value=Decimal("40")), entry("E2", value=Decimal("60"))],
    )
    assert rows == []


def test_messy_references_normalize():
    assert normalize_ref("rec1034") == "REC-1034"
    assert normalize_ref(" REC - 1070 ") == "REC-1070"
    assert normalize_ref("1112") == "REC-1112"


def test_clean_row_has_no_disagreement():
    assert compare({"REC-1": record()}, [entry()]) == []


def test_location_mismatch():
    rows = compare({"REC-1": record(location="L1")}, [entry(location="L2")])
    assert "LOCATION_MISMATCH" in reasons(rows)


def test_date_mismatch():
    rows = compare({"REC-1": record(date="2026-03-01")}, [entry(date="2026-03-02")])
    assert "DATE_MISMATCH" in reasons(rows)


def test_indian_style_amount_parses_exactly():
    assert parse_amount("1,25,400.00") == Decimal("125400.00")


def test_voided_record_is_ignored():
    rows = compare({"REC-1": record(state="VOIDED")}, [entry(value=Decimal("1"))])
    assert rows == []
