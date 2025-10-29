from sqlalchemy import ARRAY, Column, DateTime, Integer, String, func
from sqlalchemy.orm import relationship

from core.database import Base


class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    degrees = Column(ARRAY(String), nullable=True)
    specialization = Column(String, nullable=True, index=True)
    designation = Column(String, nullable=True)
    affiliated_hospital = Column(String(255), nullable=True)
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    # Relationships
    chambers = relationship(
        "DoctorChamber", back_populates="doctor", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Doctor(name={self.full_name}, specialization={self.specialization})>"
