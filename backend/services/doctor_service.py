from models.doctor import Doctor
from repositories.doctor_repository import doctor_repository
from schemas.doctor_schema import DoctorCreate, DoctorSearch, DoctorUpdate
from sqlalchemy.orm import Session


class DoctorService:
    @staticmethod
    def get_doctor_by_id(db: Session, doctor_id: int):
        doctor = doctor_repository.get_details(db, id=doctor_id)
        if not doctor:
            raise Exception("Doctor not found")
        return doctor

    @staticmethod
    def search_doctors(
        db: Session, search_params: DoctorSearch, skip: int = 0, limit: int = 100
    ) -> list[Doctor]:
        return doctor_repository.search(
            db, search_params=search_params, skip=skip, limit=limit
        )
