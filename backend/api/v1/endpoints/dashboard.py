from core.database import DbSession
from core.limiter import limiter
from fastapi import APIRouter, Cookie, Depends, HTTPException, Request
from schemas.dashboard_stats_schema import DashboardStats
from services.dashboard_service import get_chamber_count, get_doctor_count
from services.dependencies.auth_dependencies import get_current_user, require_roles
from sqlalchemy.orm import Session

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats", response_model=DashboardStats)
@limiter.limit("50/minute")
def get_dashboard_stats(db: DbSession) -> DashboardStats:
    return DashboardStats(
        doctor_count=get_doctor_count(db), chamber_count=get_chamber_count(db)
    )
