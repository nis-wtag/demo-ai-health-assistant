from core.database import get_db
from fastapi import APIRouter, Cookie, Depends, HTTPException, Request
from schemas.doctor_schema import DoctorRead, DoctorSearch
from services import doctor_service
from services.dependencies.auth_dependencies import get_current_user, require_roles
from sqlalchemy.orm import Session

router = APIRouter(prefix="/doctors", tags=["Doctors"])


@router.get("/", response_model=list[DoctorRead])
def get_doctors(
    offset: int = 0, limit: int = 10, db: Session = Depends(get_db)
) -> list[DoctorRead]:
    return doctor_service.get_doctors(db, offset=offset, limit=limit)


@router.get("/{doctor_id}", response_model=DoctorRead)
def get_doctor_details(doctor_id: int, db: Session = Depends(get_db)) -> DoctorRead:
    return doctor_service.get_doctor_by_id(db, doctor_id=doctor_id)


@router.post("/search", response_model=list[DoctorRead])
def search_doctors(
    search_params: DoctorSearch, db: Session = Depends(get_db)
) -> list[DoctorRead]:
    return doctor_service.search_doctors(db, search_params=search_params, limit=5)
