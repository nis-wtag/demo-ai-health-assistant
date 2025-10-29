from core.database import DbSession
from core.limiter import limiter
from fastapi import APIRouter, Depends, Request
from models.user import User
from schemas.dashboard_stats_schema import DashboardStats
from services.dashboard_service import get_chamber_count, get_doctor_count
from services.dependencies.auth_dependencies import get_current_user

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get(
    "/stats",
    response_model=DashboardStats,
    summary="Retrieve stats about Doctors and Chambers",
)
@limiter.limit("50/minute")
def get_dashboard_stats(
    request: Request, db: DbSession, current_user: User = Depends(get_current_user)
) -> DashboardStats:
    return DashboardStats(
        doctor_count=get_doctor_count(db), chamber_count=get_chamber_count(db)
    )
