from django.http import JsonResponse
from rest_framework.decorators import api_view

from .compare import compare
from .models import SystemARecord, SystemBEntry


@api_view(["GET"])
def disagreement_view(request):
    org = request.GET.get("org")
    if not org:
        return JsonResponse({"error": "org is required"}, status=400)

    a_rows = {}
    for record in SystemARecord.objects.select_related("location"):
        if record.location and record.location.org_id == org:
            a_rows[record.record_id] = {
                "total": record.total_value,
                "location": record.location.location_id,
                "date": record.event_date,
                "state": record.state,
            }

    b_rows = []
    for entry in SystemBEntry.objects.select_related("location"):
        b_rows.append({
            "entry_id": entry.entry_id,
            "ref": entry.record_ref,
            "value": entry.value,
            "location": entry.location.location_id if entry.location else None,
            "date": entry.recorded_on,
        })

    disagreements = compare(a_rows, b_rows)
    reason = request.GET.get("reason")
    if reason:
        disagreements = [row for row in disagreements if row["reason"] == reason]

    output = []
    for row in disagreements:
        a_record = SystemARecord.objects.select_related("location").filter(record_id=row["record_id"]).first()
        entry = SystemBEntry.objects.select_related("location").filter(entry_id=row.get("entry_id")).first() if row.get("entry_id") else None

        if a_record and a_record.location:
            source_org = a_record.location.org_id
        elif entry and entry.location:
            source_org = entry.location.org_id
        else:
            continue

        if source_org != org:
            continue

        b_location = row.get("b_location")
        if b_location:
            b_location_obj = next(
                (candidate.location for candidate in SystemBEntry.objects.select_related("location") if candidate.location and candidate.location.location_id == b_location),
                None,
            )
            if b_location_obj and b_location_obj.org_id != org:
                b_location = None

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
    if sort:
        descending = sort.startswith("-")
        output.sort(key=lambda row: row["a_value"] or "", reverse=descending)

    return JsonResponse({"rows": output})
