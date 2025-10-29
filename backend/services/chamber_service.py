from repositories.chamber_repository import chamber_repository
from schemas.chamber_schema import ChamberCreate, ChamberUpdate
from sqlalchemy.orm import Session


def get_chambers(db: Session, offset: int, limit: int):
    return chamber_repository.get_multi(db, skip=offset, limit=limit)


def get_chamber_by_id(db: Session, chamber_id: int):
    chamber = chamber_repository.get(db, id=chamber_id)
    if not chamber:
        raise Exception("Chamber not found")
    return chamber


def add_chamber(db: Session, chamber_data: ChamberCreate):
    return chamber_repository.create(db=db, obj_in=chamber_data)


def update_chamber(db: Session, chamber_id: int, chamber_data: ChamberUpdate):
    return chamber_repository.update(db=db, obj_id=chamber_id, obj_in=chamber_data)


def search_chambers(db: Session, params: str):
    return chamber_repository.search_chambers(db=db, params=params)


def delete_chamber(db: Session, chamber_id: int):
    chamber_repository.remove(db, id=chamber_id)
