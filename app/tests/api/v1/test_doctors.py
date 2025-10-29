import pytest
from fastapi import status
from fastapi.testclient import TestClient
from models.chamber import Chamber
from models.doctor import Doctor
from models.doctor_chamber import DAY, DoctorChamber, DoctorChamberVisitingHour
from sqlalchemy.orm import Session


@pytest.fixture(scope="function")
def test_doctor(db_session: Session):
    doctor = Doctor(
        full_name="Dr. Alice Smith",
        specialization="Cardiology",
        designation="Professor",
    )

    db_session.add(doctor)
    db_session.commit()
    db_session.refresh(doctor)

    yield doctor

    db_session.delete(doctor)
    db_session.commit()


@pytest.fixture(scope="function")
def seeded_doctors(db_session: Session):
    # Create Chambers
    chamber1 = Chamber(
        chamber_name="Popular Diagnostic, Dhanmondi",
        address="Dhanmondi, Dhaka",
    )
    chamber2 = Chamber(
        chamber_name="Square Hospital",
        address="Panthapath, Dhaka",
    )
    db_session.add_all([chamber1, chamber2])
    db_session.flush()

    # Create Doctors
    doctor1 = Doctor(
        full_name="Dr. Alice Smith",
        specialization="Cardiology",
        designation="Professor",
    )
    doctor2 = Doctor(
        full_name="Dr. Bob Johnson",
        specialization="Urology",
        designation="Consultant",
    )
    db_session.add_all([doctor1, doctor2])
    db_session.flush()

    link1 = DoctorChamber(
        doctor_id=doctor1.id, chamber_id=chamber1.id, contact_number="12345"
    )
    db_session.add(link1)
    db_session.flush()

    link2 = DoctorChamber(
        doctor_id=doctor2.id, chamber_id=chamber1.id, contact_number="67890"
    )
    db_session.add(link2)
    db_session.flush()

    link3 = DoctorChamber(
        doctor_id=doctor2.id, chamber_id=chamber2.id, contact_number="13579"
    )
    db_session.add(link3)
    db_session.flush()

    vh1 = DoctorChamberVisitingHour(
        doctor_chamber_id=link1.id,
        day=DAY.MONDAY,
    )
    vh2 = DoctorChamberVisitingHour(
        doctor_chamber_id=link1.id,
        day=DAY.WEDNESDAY,
    )
    db_session.add_all([vh1, vh2])
    db_session.flush()

    vh3 = DoctorChamberVisitingHour(
        doctor_chamber_id=link2.id,
        day=DAY.FRIDAY,
    )
    vh4 = DoctorChamberVisitingHour(
        doctor_chamber_id=link2.id,
        day=DAY.TUESDAY,
    )
    db_session.add_all([vh3, vh4])
    db_session.flush()

    return [doctor1, doctor2]


def test_doctor_by_specialty(client: TestClient, seeded_doctors, authenticated_user):
    DOCTOR_SEARCH_API_URL = "/api/v1/doctors/search"

    response = client.post(DOCTOR_SEARCH_API_URL, json={"specialization": "Cardiology"})

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data[0]["full_name"] == "Dr. Alice Smith"
    assert data[0]["specialization"] == "Cardiology"


def test_doctor_by_visiting_day(client: TestClient, seeded_doctors, authenticated_user):
    """
    Test: Search by visiting day should return doctors available on that day.
    Dr. Bob Johnson is available on FRIDAY.
    """
    DOCTOR_SEARCH_API_URL = "/api/v1/doctors/search"
    response = client.post(DOCTOR_SEARCH_API_URL, json={"visiting_day": "Friday"})

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["full_name"] == "Dr. Bob Johnson"


def test_doctor_by_specialty_and_day(
    client: TestClient, seeded_doctors, authenticated_user
):
    """
    Test: Search by a combination of criteria.
    Cardiology + MONDAY should return Dr. Alice Smith.
    """
    DOCTOR_SEARCH_API_URL = "/api/v1/doctors/search"
    response = client.post(
        DOCTOR_SEARCH_API_URL,
        json={"specialization": "Cardiology", "visiting_day": "Monday"},
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["full_name"] == "Dr. Alice Smith"


def test_doctor_search_no_results(
    client: TestClient, seeded_doctors, authenticated_user
):
    """
    Test: Search with criteria that match no doctors should return an empty list.
    Cardiology + FRIDAY should yield no results.
    """
    DOCTOR_SEARCH_API_URL = "/api/v1/doctors/search"
    response = client.post(
        DOCTOR_SEARCH_API_URL,
        json={"specialization": "Cardiology", "visiting_day": "Friday"},
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 0


def test_doctor_search_empty_body(
    client: TestClient, seeded_doctors, authenticated_user
):
    """
    Test: An empty search body should return all doctors (respecting the default limit).
    Our fixture has 2 doctors, the endpoint limit is 5.
    """
    DOCTOR_SEARCH_API_URL = "/api/v1/doctors/search"
    response = client.post(DOCTOR_SEARCH_API_URL, json={})  # Empty JSON

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 2


def test_doctor_by_designation(client: TestClient, seeded_doctors, authenticated_user):
    """
    Test: Search by designation.
    "Professor" should return Dr. Alice Smith.
    """
    DOCTOR_SEARCH_API_URL = "/api/v1/doctors/search"
    response = client.post(DOCTOR_SEARCH_API_URL, json={"designation": "Professor"})

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) == 1
    assert data[0]["full_name"] == "Dr. Alice Smith"


def test_get_doctor_details_success(
    client: TestClient, authenticated_user, test_doctor
):
    response = client.get(f"/api/v1/doctors/{test_doctor.id}")

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == test_doctor.id
    assert data["full_name"] == test_doctor.full_name

def test_get_doctor_details_not_found(
    client: TestClient, authenticated_user
):
    response = client.get("/api/v1/doctors/999")

    assert response.status_code == status.HTTP_404_NOT_FOUND
