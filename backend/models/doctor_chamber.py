import enum

from core.database import Base
from sqlalchemy import Column, Enum, ForeignKey, Integer, String, Time
from sqlalchemy.orm import relationship


class DAY(enum.Enum):
    SATURDAY = "Saturday"
    SUNDAY = "Sunday"
    MONDAY = "Monday"
    TUESDAY = "Tuesday"
    WEDNESDAY = "Wednesday"
    THURSDAY = "Thursday"
    FRIDAY = "Friday"


class DoctorChamberVisitingHour(Base):
    __tablename__ = "doctor_chamber_visiting_hours"

    id = Column(Integer, primary_key=True)
    doctor_chamber_id = Column(
        Integer, ForeignKey("doctor_chambers.id", ondelete="CASCADE")
    )
    day = Column(Enum(DAY), nullable=False)
    start_time = Column(Time, nullable=True)
    end_time = Column(Time, nullable=True)

    # Relationship
    doctor_chamber = relationship("DoctorChamber", back_populates="visiting_hours")


class DoctorChamber(Base):
    __tablename__ = "doctor_chambers"

    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey("doctors.id", ondelete="CASCADE"))
    chamber_id = Column(Integer, ForeignKey("chambers.id", ondelete="CASCADE"))
    contact_number = Column(String(50))

    # Relationships
    doctor = relationship("Doctor", back_populates="chambers")
    chamber = relationship("Chamber", back_populates="doctors")
    visiting_hours = relationship(
        "DoctorChamberVisitingHour",
        back_populates="doctor_chamber",
        cascade="all, delete-orphan",
    )

    @property
    def chamber_name(self):
        return self.chamber.chamber_name

    @property
    def address(self):
        return self.chamber.address

    @property
    def longitude(self):
        return self.chamber.longitude

    @property
    def latitude(self):
        return self.chamber.latitude

    def __repr__(self):
        return (
            f"<DoctorChamber(doctor_id={self.doctor_id}, chamber_id={self.chamber_id})>"
        )
