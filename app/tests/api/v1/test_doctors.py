import pytest
from fastapi import status
from fastapi.testclient import TestClient
from models.chamber import Chamber
from models.doctor import Doctor
from models.doctor_chamber import DAY, DoctorChamber, DoctorChamberVisitingHour
from sqlalchemy.orm import Session


@pytest.fixture(scope="function")
def seeded_doctor(db_session: Session):
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
        doctor_id=doctor1.id, chamber_id=chamber1.id, contract_number="12345"
    )
    db_session.add(link1)
    db_session.flush()

    link2 = DoctorChamber(
        doctor_id=doctor2.id, chamber_id=chamber1.id, contract_number="67890"
    )
    db_session.add(link2)
    db_session.flush()

    link3 = DoctorChamber(
        doctor_id=doctor2.id, chamber_id=chamber2.id, contract_number="13579"
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

    vh3 = DoctorChamberVisitingHour(
        doctor_chamber_id=link2.id,
        day=DAY.FRIDAY,
    )
    vh4 = DoctorChamberVisitingHour(
        doctor_chamber_id=link2.id,
        day=DAY.TUESDAY,
    )
    db_session.add_all([vh3, vh4])

    return [doctor1, doctor2]


