from core.database import Base
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, func


class Session(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    access_token = Column(String, unique=True, nullable=False)
    access_expires_at = Column(DateTime(timezone=True), nullable=False)

    refresh_token = Column(String, unique=True, nullable=False)
    refresh_expires_at = Column(DateTime(timezone=True), nullable=False)

    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)

    is_valid = Column(Boolean, default=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_accessed_at = Column(DateTime(timezone=True), onupdate=func.now())
