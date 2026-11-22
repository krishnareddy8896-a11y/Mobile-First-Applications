import pytest
from django.test import Client

from reconcile.models import Location, SystemARecord, SystemBEntry


@pytest.mark.django_db
def test_org_a_api_contains_no_org_b_location_or_record():
    a_location = Location.objects.create(location_id="LOC-101", org_id="ORG-A")
    b_location = Location.objects.create(location_id="LOC-201", org_id="ORG-B")
    SystemARecord.objects.create(
        record_id="REC-A",
        location=a_location,
        total_value="100.00",
        state="CONFIRMED",
    )
    SystemBEntry.objects.create(
        entry_id="E-CROSS",
        record_ref="REC-A",
        record_ref_raw="REC-A",
        location=b_location,
        value="90.00",
    )
    SystemBEntry.objects.create(
        entry_id="E-B",
        record_ref="REC-B",
        record_ref_raw="REC-B",
        location=b_location,
        value="20.00",
    )

    response = Client().get("/api/disagreements/", {"org": "ORG-A"})
    body = response.json()
    text = str(body)
    assert "LOC-201" not in text
    assert "REC-B" not in text
    assert "REC-A" in text


@pytest.mark.django_db
def test_org_b_api_contains_no_org_a_location_or_record():
    a_location = Location.objects.create(location_id="LOC-101", org_id="ORG-A")
    b_location = Location.objects.create(location_id="LOC-201", org_id="ORG-B")
    SystemARecord.objects.create(
        record_id="REC-A",
        location=a_location,
        total_value="100.00",
        state="CONFIRMED",
    )
    SystemBEntry.objects.create(
        entry_id="E-CROSS",
        record_ref="REC-A",
        record_ref_raw="REC-A",
        location=b_location,
        value="90.00",
    )
    SystemBEntry.objects.create(
        entry_id="E-B",
        record_ref="REC-B",
        record_ref_raw="REC-B",
        location=b_location,
        value="20.00",
    )

    response = Client().get("/api/disagreements/", {"org": "ORG-B"})
    body = response.json()
    text = str(body)
    assert "LOC-101" not in text
    assert "REC-A" not in text
