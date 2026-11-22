from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from reconcile.importer import import_a, import_b, import_locations


class Command(BaseCommand):
    help = "Import locations, System A, and System B CSV files"

    def handle(self, *args, **options):
        data_dir = Path(__file__).resolve().parents[3] / "data"
        locations = data_dir / "locations.csv"
        system_a = data_dir / "system_a.csv"
        system_b = data_dir / "system_b.csv"

        missing = [str(path) for path in (locations, system_a, system_b) if not path.exists()]
        if missing:
            raise CommandError("Missing CSV files: " + ", ".join(missing))

        location_counts = import_locations(locations)
        a_counts = import_a(system_a)
        b_counts = import_b(system_b)

        self.stdout.write(
            f"Locations: {location_counts[0]} read, {location_counts[1]} saved; "
            f"A: {a_counts[0]} read, {a_counts[1]} saved; "
            f"B: {b_counts[0]} read, {b_counts[1]} saved; "
            f"values left empty: {b_counts[2]}; refs cleaned: {b_counts[3]}"
        )
