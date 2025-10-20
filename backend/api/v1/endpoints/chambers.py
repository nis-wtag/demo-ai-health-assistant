from core.database import get_db
from fastapi import APIRouter, Cookie, Depends, HTTPException, Request
from schemas.chamber_schema import ChamberRead
from services import chamber_service
from services.dependencies.auth_dependencies import get_current_user, require_roles
from sqlalchemy.orm import Session

router = APIRouter(prefix="/chambers", tags=["Chambers"])


@router.get("/", response_model=list[ChamberRead])
def get_chambers(
    offset: int = 0, limit: int = 10, db: Session = Depends(get_db)
) -> list[ChamberRead]:
    return chamber_service.get_chambers(db, offset=offset, limit=limit)


@router.get("/{chamber_id}", response_model=ChamberRead)
def get_chamber_details(chamber_id: int, db: Session = Depends(get_db)) -> ChamberRead:
    return chamber_service.get_chamber_by_id(db, chamber_id=chamber_id)
