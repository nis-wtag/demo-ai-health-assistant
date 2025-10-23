from core.exceptions import AppException
from repositories.chamber_repository import chamber_repository
from repositories.doctor_repository import doctor_repository
from sqlalchemy.orm import Session


def get_doctor_count(db: Session):
    try:
        return doctor_repository.get_count(db)
    except Exception:
        raise AppException(detail="Failed to retrieve doctor count")


def get_chamber_count(db: Session):
    try:
        return chamber_repository.get_count(db)
    except Exception:
        raise AppException(detail="Failed to retrieve chamber count")
