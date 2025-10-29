from datetime import time
from typing import List, Optional

from models.doctor_chamber import DAY
from pydantic import BaseModel


class VisitingHour(BaseModel):
    day: DAY
    start_time: Optional[time] = None
    end_time: Optional[time] = None


class Chamber(BaseModel):
    chamber_name: str
    address: str
    longitude: Optional[float] = None
    latitude: Optional[float] = None
    contact_number: Optional[str] = None
    visiting_hour: Optional[List[VisitingHour]] = []


class DoctorBase(BaseModel):
    full_name: str
    degrees: Optional[List[str]] = []
    specialization: Optional[str] = []
    designation: Optional[str] = []
    affiliated_hospital: Optional[str] = None
    chambers: Optional[List[Chamber]] = []


class DoctorCreate(DoctorBase):
    pass


class DoctorUpdate(BaseModel):
    full_name: Optional[str]
    degrees: Optional[List[str]]
    specialization: Optional[str]
    designation: Optional[str]
    affiliated_hospital: Optional[str]
    chambers: Optional[List[Chamber]]


class DoctorRead(DoctorBase):
    id: int

    class Config:
        orm_mode = True
