from models.doctor import Doctor as DoctorModel
from models.doctor_chamber import DoctorChamber, DoctorChamberVisitingHour
from schemas.doctor_schema import DoctorCreate, DoctorSearch, DoctorUpdate
from sqlalchemy import and_, func
from sqlalchemy.orm import Session, selectinload
from sqlalchemy.sql import exists

from repositories.base_repository import BaseRepository


class DoctorRepository(BaseRepository[DoctorModel, DoctorCreate, DoctorUpdate]):
    def get_details(self, db: Session, id: int) -> DoctorModel | None:
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

    def search(self, db: Session, params: str):
        search_term = f"%{params}%"
        return (
            db.query(self.model)
            .filter(
                (self.model.full_name.ilike(search_term))
                | (self.model.specialization.ilike(search_term))
                | (self.model.designation.ilike(search_term))
            )
            .limit(10)
            .all()
        )

    def formatted_search(
        self, db: Session, search_params: DoctorSearch, skip: int = 0, limit: int = 5
    ) -> list[DoctorModel]:
        query = (
            db.query(self.model)
            .distinct()
            .options(
                selectinload(self.model.chambers).selectinload(DoctorChamber.chamber),
                selectinload(self.model.chambers).selectinload(
                    DoctorChamber.visiting_hours
                ),
            )
        )

        # Full-text search setup
        query_terms = []
        if search_params.full_name:
            query_terms.append(search_params.full_name.lower())
        if search_params.degrees:
            query_terms.extend(deg.lower() for deg in search_params.degrees)
        if search_params.specialization:
            query_terms.append(search_params.specialization.lower())
        if search_params.designation:
            query_terms.append(search_params.designation.lower())
        if search_params.affiliated_hospital:
            query_terms.append(search_params.affiliated_hospital.lower())
        if search_params.chamber_name:
            query_terms.append(search_params.chamber_name.lower())
        if search_params.chamber_address:
            query_terms.append(search_params.chamber_address.lower())

        # Apply FTS if terms exist
        if query_terms:
            ts_query = func.plainto_tsquery("english", " ".join(query_terms))
            query = query.filter(self.model.search_vector.op("@@")(ts_query))

        # Visiting hours filter (keep — structural logic)
        if any(
            [
                search_params.visiting_day,
                search_params.visiting_start_time,
                search_params.visiting_end_time,
            ]
        ):
            vh_exists = exists().where(
                DoctorChamberVisitingHour.doctor_chamber_id == DoctorChamber.id,
                DoctorChamber.doctor_id == self.model.id,
            )
            if search_params.visiting_day:
                vh_exists = vh_exists.where(
                    DoctorChamberVisitingHour.day == search_params.visiting_day
                )
            if search_params.visiting_start_time and search_params.visiting_end_time:
                vh_exists = vh_exists.where(
                    and_(
                        DoctorChamberVisitingHour.start_time
                        <= search_params.visiting_end_time,
                        DoctorChamberVisitingHour.end_time
                        >= search_params.visiting_start_time,
                    )
                )
            elif search_params.visiting_start_time:
                vh_exists = vh_exists.where(
                    DoctorChamberVisitingHour.start_time
                    <= search_params.visiting_start_time
                )
            query = query.filter(vh_exists)

        # Pagination
        query = query.offset(skip).limit(limit)

        return query.all()


doctor_repository = DoctorRepository(DoctorModel)
