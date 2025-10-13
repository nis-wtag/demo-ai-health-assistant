from core.database import get_db
from fastapi import APIRouter, Cookie, Depends, HTTPException, Request
from schemas.doctor_schema import DoctorRead, DoctorSearch
from services.dependencies.auth_dependencies import get_current_user, require_roles
from services.doctor_service import DoctorService
from sqlalchemy.orm import Session

router = APIRouter(prefix="/doctors", tags=["Doctors"])


@router.get("/{doctor_id}", response_model=DoctorRead)
def get_doctor_details(doctor_id: int, db: Session = Depends(get_db)) -> DoctorRead:
    return DoctorService.get_doctor_by_id(db, doctor_id=doctor_id)


@router.post("/search", response_model=list[DoctorRead])
def search_doctors(
    search_params: DoctorSearch, db: Session = Depends(get_db)
) -> list[DoctorRead]:
    return DoctorService.search_doctors(db, search_params=search_params, limit=5)
