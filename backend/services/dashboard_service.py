from repositories.chamber_repository import chamber_repository 
from repositories.doctor_repository import doctor_repository
from sqlalchemy.orm import Session


def get_doctor_count(db: Session):
    return doctor_repository.get_count(db)


def get_chamber_count(db: Session):
    return chamber_repository.get_count(db)