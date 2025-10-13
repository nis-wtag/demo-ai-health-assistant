from models.doctor import Doctor
from models.doctor_chamber import DoctorChamber
from schemas.doctor_schema import DoctorCreate, DoctorSearch, DoctorUpdate
from sqlalchemy.orm import Session, selectinload

from repositories.base_repository import BaseRepository


class DoctorRepository(BaseRepository[Doctor, DoctorCreate, DoctorUpdate]):
    def get_details(self, db: Session, id: int) -> Doctor | None:
        return (
            db.query(self.model)
            .filter(self.model.id == id)
            .options(
                selectinload(self.model.chambers).selectinload(DoctorChamber.chamber),
                selectinload(self.model.chambers).selectinload(
                    DoctorChamber.visiting_hours
                ),
            )
            .first()
        )

    def search(
        self, db: Session, search_params: DoctorSearch, skip: int = 0, limit: int = 5
    ) -> list[Doctor]:
        query = db.query(self.model).distinct()

        query = query.options(
            selectinload(self.model.chambers).selectinload(DoctorChamber.chamber),
            selectinload(self.model.chambers).selectinload(
                DoctorChamber.visiting_hours
            ),
        )

        # Doctor profile filters
        if search_params.full_name:
            query = query.filter(
                self.model.full_name.ilike(f"%{search_params.full_name}%")
            )
        if search_params.degrees:
            query = query.filter(self.model.degrees.overlap(search_params.degrees))
        if search_params.specialization:
            query = query.filter(
                self.model.specialization.ilike(f"%{search_params.specialization}%")
            )
        if search_params.designation:
            query = query.filter(
                self.model.designation.ilike(f"%{search_params.designation}%")
            )
        if search_params.affiliated_hospital:
            query = query.filter(
                self.model.affiliated_hospital.ilike(
                    f"%{search_params.affiliated_hospital}%"
                )
            )

        query = query.offset(skip).limit(limit)

        return query.all()


doctor_repository = DoctorRepository(Doctor)
