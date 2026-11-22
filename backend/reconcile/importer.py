import csv
from datetime import datetime
from pathlib import Path

from django.db import transaction

from .cleaning import normalize_ref, parse_amount
from .models import Location, SystemARecord, SystemBEntry


def parse_date(raw):
    text = (raw or "").strip()
    if not text:
        return None
    for format_string in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(text, format_string).date()
        except ValueError:
            pass
    return None


def clean_row(row):
    return {key: (value.strip() if isinstance(value, str) else value) for key, value in row.items()}


@transaction.atomic
def import_locations(path):
    read_count = saved_count = 0
    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        for row in csv.DictReader(handle):
            read_count += 1
            row = clean_row(row)
            location_id = row.get("location_id") or None
            if not location_id:
                continue
            Location.objects.update_or_create(
                location_id=location_id,
                defaults={"org_id": row.get("org_id") or "", "name": row.get("name") or ""},
            )
            saved_count += 1
    return read_count, saved_count


@transaction.atomic
def import_a(path):
    read_count = saved_count = 0
    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        for row in csv.DictReader(handle):
            read_count += 1
            row = clean_row(row)
            record_id = row.get("record_id")
            if not record_id:
                continue
            location = Location.objects.filter(location_id=row.get("location_id")).first()
            SystemARecord.objects.update_or_create(
                record_id=record_id,
                defaults={
                    "location": location,
                    "event_date": parse_date(row.get("event_date")),
                    "category_code": row.get("category_code") or "",
                    "actor_id": row.get("actor_id") or None,
                    "base_value": parse_amount(row.get("base_value")),
                    "adjustment": parse_amount(row.get("adjustment")),
                    "total_value": parse_amount(row.get("total_value")),
                    "state": row.get("state") or "",
                },
            )
            saved_count += 1
    return read_count, saved_count


@transaction.atomic
def import_b(path):
    read_count = saved_count = 0
    values_empty = refs_cleaned = 0
    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        for row in csv.DictReader(handle):
            read_count += 1
            row = clean_row(row)
            entry_id = row.get("entry_id")
            if not entry_id:
                continue
            raw_ref = row.get("record_ref")
            cleaned_ref = normalize_ref(raw_ref)
            if raw_ref and cleaned_ref and raw_ref != cleaned_ref:
                refs_cleaned += 1
            raw_value = row.get("value")
            value = parse_amount(raw_value)
            if value is None:
                values_empty += 1
            location = Location.objects.filter(location_id=row.get("location_id")).first()
            SystemBEntry.objects.update_or_create(
                entry_id=entry_id,
                defaults={
                    "record_ref_raw": raw_ref or "",
                    "record_ref": cleaned_ref,
                    "location": location,
                    "recorded_on": parse_date(row.get("recorded_on")),
                    "value_raw": raw_value or "",
                    "value": value,
                    "label": row.get("label") or "",
                },
            )
            saved_count += 1
    return read_count, saved_count, values_empty, refs_cleaned
