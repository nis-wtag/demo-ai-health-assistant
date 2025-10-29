from datetime import time
from typing import List, Optional

from models.doctor_chamber import DAY
from pydantic import BaseModel, ConfigDict


class VisitingHour(BaseModel):
    day: DAY
    start_time: Optional[time] = None
    end_time: Optional[time] = None

    model_config = ConfigDict(from_attributes=True)


class Chamber(BaseModel):
    id: int
    chamber_name: str
    address: str
    longitude: Optional[float] = None
    latitude: Optional[float] = None
    contact_number: Optional[str] = None
    visiting_hours: Optional[List[VisitingHour]] = []

    model_config = ConfigDict(from_attributes=True)


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

    model_config = ConfigDict(from_attributes=True)


class DoctorSearch(BaseModel):
    full_name: Optional[str] = None
    degrees: Optional[List[str]] = None
    specialization: Optional[str] = None
    designation: Optional[str] = None
    affiliated_hospital: Optional[str] = None
    chamber_name: Optional[str] = None
    chamber_address: Optional[str] = None
    visiting_day: Optional[DAY] = None
    visiting_start_time: Optional[time] = None
    visiting_end_time: Optional[time] = None
