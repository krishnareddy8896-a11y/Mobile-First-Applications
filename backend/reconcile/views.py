from decimal import Decimal

from django.http import JsonResponse
from rest_framework.decorators import api_view

from .compare import compare
from .models import SystemARecord, SystemBEntry


@api_view(["GET"])
def disagreement_view(request):
    org = request.GET.get("org")
    if not org:
        return JsonResponse({"error": "org is required"}, status=400)

    a_records = list(SystemARecord.objects.select_related("location"))
    a_by_id = {record.record_id: record for record in a_records}
    a_rows = {
        record.record_id: {
            "total": record.total_value,
            "location": record.location.location_id if record.location else None,
            "date": record.event_date,
            "state": record.state,
        }
        for record in a_records
    }

    b_entries = list(SystemBEntry.objects.select_related("location"))
    b_by_id = {entry.entry_id: entry for entry in b_entries}
    b_rows = [
        {
            "entry_id": entry.entry_id,
            "ref": entry.record_ref,
            "value": entry.value,
            "location": entry.location.location_id if entry.location else None,
            "date": entry.recorded_on,
        }
        for entry in b_entries
    ]

    disagreements = compare(a_rows, b_rows)
    reason = request.GET.get("reason")
    if reason:
        disagreements = [row for row in disagreements if row["reason"] == reason]

    output = []
    for row in disagreements:
        a_record = a_by_id.get(row["record_id"])
        entry = b_by_id.get(row.get("entry_id"))

        if a_record and a_record.location:
            source_org = a_record.location.org_id
        elif entry and entry.location:
            source_org = entry.location.org_id
        else:
            continue

        if source_org != org:
            continue

        b_location = (
            entry.location.location_id
            if entry and entry.location and entry.location.org_id == org
            else None
        )

        difference = None
        if row["a_value"] is not None and row["b_value"] is not None:
            difference = row["a_value"] - row["b_value"]
        output.append({
            "reason": row["reason"],
            "record_id": row["record_id"],
            "location": row["location"],
            "a_value": str(row["a_value"]) if row["a_value"] is not None else "",
            "b_value": str(row["b_value"]) if row["b_value"] is not None else "",
            "difference": str(difference) if difference is not None else "",
            "b_location": b_location,
        })

    sort = request.GET.get("sort")
    if sort and sort.lstrip("-") == "value":
        descending = sort.startswith("-")
        populated = [row for row in output if row["a_value"]]
        empty = [row for row in output if not row["a_value"]]
        populated.sort(key=lambda row: Decimal(row["a_value"]), reverse=descending)
        output = populated + empty

    return JsonResponse({"rows": output})
