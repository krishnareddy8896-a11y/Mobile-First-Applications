import csv
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from reconcile.importer import import_a, import_b, import_locations
from reconcile.models import Location, SystemARecord, SystemBEntry


def source_ids(path, column):
    with path.open("r", newline="", encoding="utf-8-sig") as handle:
        return [
            row[column].strip()
            for row in csv.DictReader(handle)
            if row.get(column) and row[column].strip()
        ]


class Command(BaseCommand):
    help = "Import locations, System A, and System B CSV files"

    @transaction.atomic
    def handle(self, *args, **options):
        data_dir = Path(__file__).resolve().parents[3] / "data"
        locations = data_dir / "locations.csv"
        system_a = data_dir / "system_a.csv"
        system_b = data_dir / "system_b.csv"

        missing = [str(path) for path in (locations, system_a, system_b) if not path.exists()]
        if missing:
            raise CommandError("Missing CSV files: " + ", ".join(missing))

        location_ids = source_ids(locations, "location_id")
        a_ids = source_ids(system_a, "record_id")
        b_ids = source_ids(system_b, "entry_id")
        location_counts = import_locations(locations)
        a_counts = import_a(system_a)
        b_counts = import_b(system_b)

        SystemBEntry.objects.exclude(entry_id__in=b_ids).delete()
        SystemARecord.objects.exclude(record_id__in=a_ids).delete()
        Location.objects.exclude(location_id__in=location_ids).delete()

        self.stdout.write(
            f"Locations: {location_counts[0]} read, {location_counts[1]} saved; "
            f"A: {a_counts[0]} read, {a_counts[1]} saved; "
            f"B: {b_counts[0]} read, {b_counts[1]} saved; "
            f"values left empty: {b_counts[2]}; refs cleaned: {b_counts[3]}"
        )
