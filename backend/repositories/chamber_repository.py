from models.chamber import Chamber as ChamberModel
from schemas.chamber_schema import ChamberCreate, ChamberUpdate
from sqlalchemy.orm import Session

from repositories.base_repository import BaseRepository


class ChamberRepository(BaseRepository[ChamberModel, ChamberCreate, ChamberUpdate]):
    def search_chambers(self, db: Session, params: str):
        search_term = f"%{params}%"
        return (
            db.query(self.model)
            .filter(
                (self.model.chamber_name.ilike(search_term))
                | (self.model.address.ilike(search_term))
            )
            .limit(10)
            .all()
        )


chamber_repository = ChamberRepository(ChamberModel)
