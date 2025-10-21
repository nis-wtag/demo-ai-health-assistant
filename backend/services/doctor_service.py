from repositories.doctor_repository import doctor_repository
from schemas.doctor_schema import DoctorCreate, DoctorRead, DoctorSearch, DoctorUpdate
from sqlalchemy.orm import Session


def get_doctors(db: Session, offset: int, limit: int):
    return doctor_repository.get_multi(db, skip=offset, limit=limit)


def get_doctor_by_id(db: Session, doctor_id: int):
    doctor = doctor_repository.get_details(db, id=doctor_id)
    if not doctor:
        raise Exception("Doctor not found")
    return doctor


def add_doctor(db: Session, doctor_data: DoctorCreate):
    return doctor_repository.create(db=db, obj_in=doctor_data)


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
    doctor_repository.remove(db, id=doctor_id)
