from collections import defaultdict


def compare(a_rows, b_rows):
    """Pure comparison: a_rows maps record IDs to record dictionaries."""
    disagreements = []
    by_ref = defaultdict(list)
    for entry in b_rows:
        by_ref[entry["ref"]].append(entry)

    for entry in b_rows:
        ref = entry["ref"]
        if ref is not None and ref not in a_rows:
            disagreements.append({
                "reason": "ORPHAN_IN_B",
                "record_id": ref,
                "entry_id": entry["entry_id"],
                "location": entry["location"],
                "a_value": None,
                "b_value": entry["value"],
                "date": entry["date"],
            })

    for record_id, record in a_rows.items():
        if record.get("state") == "VOIDED":
            continue
        entries = by_ref.get(record_id, [])
        if not entries:
            disagreements.append({
                "reason": "MISSING_IN_B",
                "record_id": record_id,
                "entry_id": None,
                "location": record["location"],
                "a_value": record["total"],
                "b_value": None,
                "date": record["date"],
            })
            continue

        values = [entry["value"] for entry in entries]
        if any(value is None for value in values):
            disagreements.append({
                "reason": "VALUE_MISMATCH",
                "record_id": record_id,
                "entry_id": entries[0]["entry_id"],
                "location": record["location"],
                "a_value": record["total"],
                "b_value": None,
                "date": record["date"],
            })
            continue

        if len(entries) > 1:
            if sum(values) != record["total"]:
                disagreements.append({
                    "reason": "DUPLICATE_IN_B",
                    "record_id": record_id,
                    "entry_id": entries[0]["entry_id"],
                    "location": record["location"],
                    "a_value": record["total"],
                    "b_value": sum(values),
                    "date": record["date"],
                })
            continue

        entry = entries[0]
        if entry["value"] != record["total"]:
            disagreements.append({
                "reason": "VALUE_MISMATCH",
                "record_id": record_id,
                "entry_id": entry["entry_id"],
                "location": record["location"],
                "a_value": record["total"],
                "b_value": entry["value"],
                "date": record["date"],
            })
        if entry["location"] != record["location"]:
            disagreements.append({
                "reason": "LOCATION_MISMATCH",
                "record_id": record_id,
                "entry_id": entry["entry_id"],
                "location": record["location"],
                "a_value": record["total"],
                "b_value": entry["value"],
                "date": record["date"],
                "b_location": entry["location"],
            })
        if entry["date"] != record["date"]:
            disagreements.append({
                "reason": "DATE_MISMATCH",
                "record_id": record_id,
                "entry_id": entry["entry_id"],
                "location": record["location"],
                "a_value": record["total"],
                "b_value": entry["value"],
                "date": record["date"],
                "b_date": entry["date"],
            })

    return disagreements
