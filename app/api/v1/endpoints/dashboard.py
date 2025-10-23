from core.database import DbSession
from core.limiter import limiter
from fastapi import APIRouter, Request
from schemas.dashboard_stats_schema import DashboardStats
from services.dashboard_service import get_chamber_count, get_doctor_count

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats", response_model=DashboardStats)
@limiter.limit("50/minute")
def get_dashboard_stats(request: Request, db: DbSession) -> DashboardStats:
    return DashboardStats(
        doctor_count=get_doctor_count(db), chamber_count=get_chamber_count(db)
    )
