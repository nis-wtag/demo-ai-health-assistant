import json
import os
import shutil
from pathlib import Path
from typing import Optional

from core.database import DbSession
from core.exceptions import AppException
from core.limiter import limiter
from fastapi import APIRouter, File, Form, Query, Request, UploadFile
from schemas.doctor_schema import DoctorBase, DoctorRead, DoctorSearch, DoctorUpdate
from services import doctor_service

router = APIRouter(prefix="/doctors", tags=["Doctors"])


UPLOAD_DIR = Path("data/doctors/image")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

MAX_FILE_SIZE = 20 * 1024 * 1024
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}


@router.get("/", response_model=list[DoctorRead])
@limiter.limit("50/minute")
def get_doctors(
    request: Request, db: DbSession, offset: int = 0, limit: int = 10
) -> list[DoctorRead]:
    return doctor_service.get_doctors(db, offset=offset, limit=limit)


@router.post("/", response_model=DoctorRead)
@limiter.limit("50/minute")
def add_doctor(
    request: Request,
    full_name: str = Form(...),
    image: Optional[UploadFile] = File(None),
    degrees: Optional[str] = Form(None),
    specialization: Optional[str] = Form(None),
    designation: Optional[str] = Form(None),
    affiliated_hospital: Optional[str] = Form(None),
    chambers: Optional[str] = Form(None),
    db: DbSession = None,
) -> DoctorRead:
    image_url = None
    if image:
        ext = image.filename.split(".")[-1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise AppException(detail=f"Invalid file type: {ext}")

        image.file.seek(0, os.SEEK_END)
        file_size = image.file.tell()
        image.file.seek(0)

        if file_size > MAX_FILE_SIZE:
            raise AppException(detail="File too large. Max 20 MB allowed.")

        filename = image.filename.replace(" ", "_")
        image_path = UPLOAD_DIR / filename
        with image_path.open("wb") as f:
            shutil.copyfileobj(image.file, f)
        image_url = f"image/{filename}"

    degree_list = [d.strip() for d in degrees.split(",")] if degrees else []

    doctor_data = DoctorBase(
        full_name=full_name,
        image=image_url,
        degrees=degree_list,
        specialization=specialization,
        designation=designation,
        affiliated_hospital=affiliated_hospital,
    )

    chamber_data = json.loads(chambers) if chambers else None

    return doctor_service.add_doctor(
        db, doctor_data=doctor_data, chamber_data=chamber_data
    )


@router.get("/search", response_model=list[DoctorRead])
@limiter.limit("50/minute")
def search_doctors(
    request: Request,
    params: str = Query(description="Search term for doctors"),
    db: DbSession = None,
) -> list[DoctorRead]:
    return doctor_service.search_doctors(db, params=params)


@router.post("/search", response_model=list[DoctorRead])
@limiter.limit("50/minute")
def formatted_search_doctors(
    request: Request, search_params: DoctorSearch, db: DbSession
) -> list[DoctorRead]:
    return doctor_service.formatted_search_doctors(
        db, search_params=search_params, limit=5
    )


@router.get("/{doctor_id}", response_model=DoctorRead)
@limiter.limit("50/minute")
def get_doctor_details(request: Request, doctor_id: int, db: DbSession) -> DoctorRead:
    return doctor_service.get_doctor_by_id(db, doctor_id=doctor_id)


@router.put("/{doctor_id}", response_model=DoctorRead)
@limiter.limit("5/minute")
def update_doctor(
    request: Request, doctor_id: int, doctor_data: DoctorUpdate, db: DbSession
) -> DoctorRead:
    return doctor_service.update_doctor(
        db=db, doctor_id=doctor_id, doctor_data=doctor_data
    )


@router.delete("/{doctor_id}")
@limiter.limit("3/minute")
def delete_doctor(request: Request, doctor_id: int, db: DbSession):
    doctor_service.delete_doctor(db, doctor_id=doctor_id)
    return {"detail": f"Doctor {doctor_id} deleted"}
