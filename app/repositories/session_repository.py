from datetime import datetime

from models.session import Session as SessionModel
from sqlalchemy.orm import Session


class SessionRepository:
    @staticmethod
    def create_session(
        db: Session,
        user_id: int,
        access_token: str,
        refresh_token: str,
        access_expires_at: datetime,
        refresh_expires_at: datetime,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> SessionModel:
        session = SessionModel(
            user_id=user_id,
            access_token=access_token,
            refresh_token=refresh_token,
            access_expires_at=access_expires_at,
            refresh_expires_at=refresh_expires_at,
            ip_address=ip_address,
            user_agent=user_agent,
            is_valid=True,
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        return session

    @staticmethod
    def invalidate_session(db: Session, session: SessionModel):
        session.is_valid = False
        db.commit()

    @staticmethod
    def get_by_access_token(db: Session, access_token: str) -> SessionModel | None:
        return (
            db.query(SessionModel)
            .filter(SessionModel.access_token == access_token, SessionModel.is_valid)
            .first()
        )

    @staticmethod
    def get_by_refresh_token(db: Session, refresh_token: str) -> SessionModel | None:
        return (
            db.query(SessionModel)
            .filter(SessionModel.refresh_token == refresh_token, SessionModel.is_valid)
            .first()
        )
