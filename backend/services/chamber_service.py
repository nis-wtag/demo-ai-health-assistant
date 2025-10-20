from repositories.chamber_repository import chamber_repository
from sqlalchemy.orm import Session


def get_chambers(db: Session, offset: int, limit: int):
    return chamber_repository.get_multi(db, skip=offset, limit=limit)


def get_chamber_by_id(db: Session, chamber_id: int):
    chamber = chamber_repository.get(db, id=chamber_id)
    if not chamber:
        raise Exception("Chamber not found")
    return chamber
