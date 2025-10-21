import shutil
from pathlib import Path
from typing import Optional

from core.database import DbSession
from fastapi import (
    APIRouter,
    Cookie,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    Request,
    UploadFile,
)
from schemas.doctor_schema import DoctorCreate, DoctorRead, DoctorSearch
from services import doctor_service
from services.dependencies.auth_dependencies import get_current_user, require_roles
from sqlalchemy.orm import Session

router = APIRouter(prefix="/doctors", tags=["Doctors"])


UPLOAD_DIR = Path("data/doctors/image")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.get("/", response_model=list[DoctorRead])
def get_doctors(db: DbSession, offset: int = 0, limit: int = 10) -> list[DoctorRead]:
    return doctor_service.get_doctors(db, offset=offset, limit=limit)


@router.post("/", response_model=DoctorRead)
def add_doctor(
    full_name: str = Form(...),
    image: Optional[UploadFile] = File(None),
    degrees: Optional[str] = Form(None),
    specialization: Optional[str] = Form(None),
    designation: Optional[str] = Form(None),
    affiliated_hospital: Optional[str] = Form(None),
    chambers: Optional[list[int]] = Form(None),
    db: DbSession = None,
) -> DoctorRead:
    try:
        image_path = None
        if image:
            filename = image.filename.replace(" ", "_")
            image_path = UPLOAD_DIR / filename
            with image_path.open("wb") as f:
                shutil.copyfileobj(image.file, f)

        doctor_data = DoctorCreate(
            full_name=full_name,
            image=str(image_path) if image_path else None,
            degrees=[d.strip() for d in degrees.split(",") if d.strip()],
            specialization=specialization,
            designation=designation,
            affiliated_hospital=affiliated_hospital
        )

        return doctor_service.add_doctor(db, doctor_data)
    except Exception as e:
        raise HTTPException(400, e)


@router.get("/search", response_model=list[DoctorRead])
def search_doctors(
    params: str = Query(description="Search term for doctors"), db: DbSession = None
) -> list[DoctorRead]:
    return doctor_service.search_doctors(db, params=params)


@router.post("/search", response_model=list[DoctorRead])
def formatted_search_doctors(
    search_params: DoctorSearch, db: DbSession
) -> list[DoctorRead]:
    return doctor_service.formatted_search_doctors(
        db, search_params=search_params, limit=5
    )


@router.get("/{doctor_id}", response_model=DoctorRead)
def get_doctor_details(doctor_id: int, db: DbSession) -> DoctorRead:
    return doctor_service.get_doctor_by_id(db, doctor_id=doctor_id)


@router.delete("/{doctor_id}")
def delete_doctor(doctor_id: int, db: DbSession):
    try:
        doctor_service.delete_doctor(db, doctor_id=doctor_id)
        return {"message": f"Doctor {doctor_id} deleted"}
    except Exception as e:
        raise HTTPException(400, e)
