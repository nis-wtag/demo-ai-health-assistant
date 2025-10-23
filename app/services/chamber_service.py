from core.exceptions import AppException
from repositories.chamber_repository import chamber_repository
from schemas.chamber_schema import ChamberCreate, ChamberUpdate
from sqlalchemy.orm import Session


def get_chambers(db: Session, offset: int, limit: int):
    try:
        return chamber_repository.get_multi(db, skip=offset, limit=limit)
    except Exception:
        raise AppException(status_code=404, detail="Chambers not found")


def get_chamber_by_id(db: Session, chamber_id: int):
    chamber = chamber_repository.get(db, id=chamber_id)
    if not chamber:
        raise AppException(status_code=404, detail="Chamber not found")
    return chamber


def add_chamber(db: Session, chamber_data: ChamberCreate):
    try:
        return chamber_repository.create(db=db, obj_in=chamber_data)
    except Exception:
        raise AppException(detail="Failed to add the chamber")


def update_chamber(db: Session, chamber_id: int, chamber_data: ChamberUpdate):
    try:
        return chamber_repository.update(db=db, obj_id=chamber_id, obj_in=chamber_data)
    except Exception:
        raise AppException(detail=f"Failed to update the chamber with ID: {chamber_id}")


def search_chambers(db: Session, params: str):
    try:
        return chamber_repository.search_chambers(db=db, params=params)
    except Exception:
        raise AppException()


def delete_chamber(db: Session, chamber_id: int):
    try:
        chamber_repository.remove(db, id=chamber_id)
    except Exception:
        raise AppException(detail="Failed to delete the chamber")
