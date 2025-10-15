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
    return SessionRepository.get_by_access_token(db, token)

def get_by_refresh_token(db, token):
    return SessionRepository.get_by_refresh_token(db, token)

def invalidate_session(db, session):
    return SessionRepository.invalidate_session(db, session)
