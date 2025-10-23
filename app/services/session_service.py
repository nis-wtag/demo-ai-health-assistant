from core.exceptions import SessionInvalidException, SessionNotFoundException
from repositories.session_repository import SessionRepository


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


def get_by_access_token(db, token):
    session = SessionRepository.get_by_access_token(db, token)
    if not session:
        raise SessionNotFoundException("No session found with this access token")
    return session


def get_by_refresh_token(db, token):
    session = SessionRepository.get_by_refresh_token(db, token)
    if not session:
        raise SessionNotFoundException("No session found with this refresh token")
    return session


def invalidate_session(db, session):
    if not session:
        raise SessionInvalidException("Cannot invalidate an empty or invalid session")
    return SessionRepository.invalidate_session(db, session)
