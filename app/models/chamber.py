from core.database import Base
from sqlalchemy import Column, DateTime, Float, Integer, String, Text, func
from sqlalchemy.orm import relationship


class Chamber(Base):
    __tablename__ = "chambers"

    id = Column(Integer, primary_key=True, index=True)
    chamber_name = Column(String(255), nullable=False, unique=True, index=True)
    address = Column(Text, nullable=False)
    longitude = Column(Float, nullable=True)
    latitude = Column(Float, nullable=True)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    # Relationships
    doctors = relationship(
        "DoctorChamber", back_populates="chamber", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Chamber(name={self.chamber_name}, address={self.address})>"
