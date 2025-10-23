from core.database import DbSession
from core.limiter import limiter
from fastapi import APIRouter, Query, Request
from schemas.chamber_schema import ChamberCreate, ChamberRead, ChamberUpdate
from services import chamber_service

router = APIRouter(prefix="/chambers", tags=["Chambers"])


@router.get("/", response_model=list[ChamberRead])
@limiter.limit("50/minute")
def get_chambers(
    request: Request, db: DbSession, offset: int = 0, limit: int = 10
) -> list[ChamberRead]:
    return chamber_service.get_chambers(db, offset=offset, limit=limit)


@router.post("/", response_model=ChamberRead)
@limiter.limit("50/minute")
def add_chamber(
    request: Request, chamber_data: ChamberCreate, db: DbSession
) -> ChamberRead:
    return chamber_service.add_chamber(db, chamber_data)


@router.get("/search", response_model=list[ChamberRead])
@limiter.limit("20/minute")
def search_chambers(
    request: Request,
    params: str = Query(description="Search term for chambers"),
    db: DbSession = None,
) -> list[ChamberRead]:
    print(params)
    return chamber_service.search_chambers(db=db, params=params)


@router.delete("/{chamber_id}")
@limiter.limit("3/minute")
def delete_chamber(request: Request, chamber_id: int, db: DbSession):
    chamber_service.delete_chamber(db, chamber_id=chamber_id)
    return {"detail": f"Chamber {chamber_id} deleted"}


@router.get("/{chamber_id}", response_model=ChamberRead)
@limiter.limit("50/minute")
def get_chamber_details(
    request: Request, chamber_id: int, db: DbSession
) -> ChamberRead:
    return chamber_service.get_chamber_by_id(db, chamber_id=chamber_id)


@router.put("/{chamber_id}", response_model=ChamberRead)
@limiter.limit("5/minute")
def update_chamber(
    request: Request, chamber_id: int, chamber_data: ChamberUpdate, db: DbSession
) -> ChamberRead:
    return chamber_service.update_chamber(
        db=db, chamber_id=chamber_id, chamber_data=chamber_data
    )
