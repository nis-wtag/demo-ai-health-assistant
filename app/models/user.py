import enum

from core.database import Base
from sqlalchemy import Column, DateTime, Enum, Integer, String, func


class UserRole(enum.Enum):
    USER = "USER"
    SUPERUSER = "SUPERUSER"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, nullable=False, unique=True, index=True)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    def __repr__(self):
        return f"<User(email='{self.email}', full_name='{self.full_name}', role='{self.role}')>"
