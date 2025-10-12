from repositories.session_repository import SessionRepository


class SessionService:
    @staticmethod
    def create_session(
        db,
        user_id,
        access_token,
        refresh_token,
        access_expires_at,
        refresh_expires_at,
        ip_address=None,
        user_agent=None,
    ):
        return SessionRepository.create_session(
            db,
            user_id,
            access_token,
            refresh_token,
            access_expires_at,
            refresh_expires_at,
            ip_address,
            user_agent,
        )

    @staticmethod
    def get_by_access_token(db, token):
        return SessionRepository.get_by_access_token(db, token)

    @staticmethod
    def get_by_refresh_token(db, token):
        return SessionRepository.get_by_refresh_token(db, token)

    @staticmethod
    def invalidate_session(db, session):
        return SessionRepository.invalidate(db, session)
