from typing import Optional

from core.exceptions import AppException, NotFoundException
from models.chamber import Chamber
from models.doctor import Doctor
from models.doctor_chamber import DoctorChamber, DoctorChamberVisitingHour
from repositories.doctor_repository import doctor_repository
from schemas.doctor_schema import (
    DoctorBase,
    DoctorRead,
    DoctorSearch,
    DoctorUpdate,
)
from sqlalchemy.orm import Session


def get_doctors(db: Session, offset: int, limit: int):
    return doctor_repository.get_multi(db, skip=offset, limit=limit)


def get_doctor_by_id(db: Session, doctor_id: int):
    doctor = doctor_repository.get_details(db, id=doctor_id)
    if not doctor:
        raise NotFoundException(detail="Doctor not found")
    return doctor


def add_doctor(
    db: Session, doctor_data: DoctorBase, chamber_data: Optional[list[dict]]
):
    doctor = Doctor(**doctor_data.model_dump())
    db.add(doctor)
    db.flush()

    if chamber_data:
        for chamber_info in chamber_data:
            chamber_id = chamber_info.get("id")
            contact_number = chamber_info.get("contact_number")
            visiting_hours = chamber_info.get("visiting_hours", [])

            chamber = db.query(Chamber).filter(Chamber.id == chamber_id).first()
            if not chamber:
                raise AppException(
                    status_code=404, detail=f"Chamber {chamber_id} not found"
                )

            doctor_chamber = DoctorChamber(
                doctor_id=doctor.id,
                chamber_id=chamber_id,
                contact_number=contact_number,
            )
            db.add(doctor_chamber)
            db.flush()

            for vh in visiting_hours:
                db.add(
                    DoctorChamberVisitingHour(
                        doctor_chamber_id=doctor_chamber.id,
                        day=vh["day"],
                        start_time=vh.get("start_time"),
                        end_time=vh.get("end_time"),
                    )
                )

    db.commit()
    db.refresh(doctor)
    return doctor


def search_doctors(db: Session, params: str):
    return doctor_repository.search(db=db, params=params)


def formatted_search_doctors(
    db: Session, search_params: DoctorSearch, skip: int = 0, limit: int = 100
) -> list[DoctorRead]:
    doctor_models = doctor_repository.formatted_search(
        db, search_params=search_params, skip=skip, limit=limit
    )
    return [DoctorRead.model_validate(doctor) for doctor in doctor_models]


def delete_doctor(db: Session, doctor_id: int):
    doctor = doctor_repository.get_details(db, doctor_id)
    if not doctor:
        raise AppException(status_code=404, detail="Doctor not found")
    doctor_repository.remove(db, id=doctor_id)


def update_doctor(db: Session, doctor_id: int, doctor_data: DoctorUpdate):
    doctor = doctor_repository.get_details(db, doctor_id)
    if not doctor:
        raise AppException(status_code=404, detail="Doctor not found")
    return doctor_repository.update(db=db, obj_id=doctor_id, obj_in=doctor_data)
