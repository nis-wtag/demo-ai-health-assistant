from models.chamber import Chamber as ChamberModel
from schemas.chamber_schema import ChamberCreate, ChamberUpdate

from repositories.base_repository import BaseRepository


class ChamberRepository(BaseRepository[ChamberModel, ChamberCreate, ChamberUpdate]):
    pass


chamber_repository = ChamberRepository(ChamberModel)
