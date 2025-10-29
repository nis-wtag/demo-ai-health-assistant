from core.database import DbSession
from fastapi import APIRouter, Cookie, Depends, HTTPException, Query, Request
from schemas.chamber_schema import ChamberCreate, ChamberRead, ChamberUpdate
from services import chamber_service
from services.dependencies.auth_dependencies import get_current_user, require_roles
from sqlalchemy.orm import Session

router = APIRouter(prefix="/chambers", tags=["Chambers"])


@router.get("/", response_model=list[ChamberRead])
def get_chambers(db: DbSession, offset: int = 0, limit: int = 10) -> list[ChamberRead]:
    return chamber_service.get_chambers(db, offset=offset, limit=limit)


@router.post("/", response_model=ChamberRead)
def add_chamber(chamber_data: ChamberCreate, db: DbSession) -> ChamberRead:
    try:
        return chamber_service.add_chamber(db, chamber_data)
    except Exception as e:
        raise HTTPException(400, e)


@router.get("/search", response_model=list[ChamberRead])
def search_chambers(
    params: str = Query(description="Search term for chambers"), db: DbSession = None
) -> list[ChamberRead]:
    print(params)
    try:
        return chamber_service.search_chambers(db=db, params=params)
    except Exception as e:
        raise HTTPException(400, e)


@router.delete("/{chamber_id}")
def delete_chamber(chamber_id: int, db: DbSession):
    try:
        chamber_service.delete_chamber(db, chamber_id=chamber_id)
        return {"message": f"Chamber {chamber_id} deleted"}
    except Exception as e:
        raise HTTPException(400, e)


@router.get("/{chamber_id}", response_model=ChamberRead)
def get_chamber_details(chamber_id: int, db: DbSession) -> ChamberRead:
    try:
        return chamber_service.get_chamber_by_id(db, chamber_id=chamber_id)
    except Exception as e:
        raise HTTPException(400, e)


@router.put("/{chamber_id}", response_model=ChamberRead)
def update_chamber(
    chamber_id: int, chamber_data: ChamberUpdate, db: DbSession
) -> ChamberRead:
    try:
        return chamber_service.update_chamber(
            db=db, chamber_id=chamber_id, chamber_data=chamber_data
        )
    except Exception as e:
        raise HTTPException(400, e)
