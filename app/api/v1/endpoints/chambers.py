from core.database import DbSession
from core.limiter import limiter
from fastapi import APIRouter, Depends, Query, Request
from models.user import User, UserRole
from schemas.chamber_schema import ChamberCreate, ChamberRead, ChamberUpdate
from services import chamber_service
from services.dependencies.auth_dependencies import get_current_user, require_roles

router = APIRouter(prefix="/chambers", tags=["Chambers"])


@router.get(
    "/",
    response_model=list[ChamberRead],
    status_code=200,
    summary="Retrieve all chambers (paginated)",
)
@limiter.limit("50/minute")
def get_chambers(
    request: Request,
    db: DbSession,
    offset: int = 0,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
) -> list[ChamberRead]:
    return chamber_service.get_chambers(db, offset=offset, limit=limit)


@router.post(
    "/", response_model=ChamberRead, status_code=201, summary="Add a new chamber"
)
@limiter.limit("50/minute")
def add_chamber(
    request: Request,
    chamber_data: ChamberCreate,
    db: DbSession,
    current_user: User = Depends(require_roles(UserRole.SUPERUSER)),
) -> ChamberRead:
    return chamber_service.add_chamber(db, chamber_data)


@router.get(
    "/search", response_model=list[ChamberRead], summary="Search chambers by keyword"
)
@limiter.limit("20/minute")
def search_chambers(
    request: Request,
    params: str = Query(description="Search term for chambers"),
    db: DbSession = None,
    current_user: User = Depends(get_current_user),
) -> list[ChamberRead]:
    print(params)
    return chamber_service.search_chambers(db=db, params=params)


@router.delete("/{chamber_id}", summary="Delete a chamber by ID")
@limiter.limit("3/minute")
def delete_chamber(
    request: Request,
    chamber_id: int,
    db: DbSession,
    current_user: User = Depends(require_roles(UserRole.SUPERUSER)),
):
    chamber_service.delete_chamber(db, chamber_id=chamber_id)
    return {"detail": f"Chamber {chamber_id} deleted"}


@router.get(
    "/{chamber_id}", response_model=ChamberRead, summary="Get chamber details by ID"
)
@limiter.limit("50/minute")
def get_chamber_details(
    request: Request,
    chamber_id: int,
    db: DbSession,
    current_user: User = Depends(get_current_user),
) -> ChamberRead:
    return chamber_service.get_chamber_by_id(db, chamber_id=chamber_id)


@router.put(
    "/{chamber_id}",
    response_model=ChamberRead,
    summary="Update existing chamber information",
)
@limiter.limit("5/minute")
def update_chamber(
    request: Request,
    chamber_id: int,
    chamber_data: ChamberUpdate,
    db: DbSession,
    current_user: User = Depends(require_roles(UserRole.SUPERUSER)),
) -> ChamberRead:
    return chamber_service.update_chamber(
        db=db, chamber_id=chamber_id, chamber_data=chamber_data
    )
