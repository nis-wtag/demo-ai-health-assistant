from datetime import time
from typing import List, Optional

from models.doctor_chamber import DAY
from pydantic import BaseModel, ConfigDict

from schemas.chamber_schema import ChamberUpdate, DoctorChamberRead


class DoctorBase(BaseModel):
    full_name: str
    image: Optional[str] = None
    degrees: Optional[List[str]] = []
    specialization: Optional[str] = None
    designation: Optional[str] = None
    affiliated_hospital: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class DoctorCreate(DoctorBase):
    chambers: Optional[List[DoctorChamberRead]] = []


class DoctorUpdate(BaseModel):
    image: Optional[str] = None
    full_name: Optional[str]
    degrees: Optional[List[str]] = []
    specialization: Optional[str] = None
    designation: Optional[str] = None
    affiliated_hospital: Optional[str] = None
    chambers: Optional[List[ChamberUpdate]] = []


class DoctorRead(DoctorBase):
    id: int
    chambers: List[DoctorChamberRead] = []

    model_config = ConfigDict(from_attributes=True)


class DoctorSearch(BaseModel):
    full_name: Optional[str] = None
    degrees: Optional[List[str]] = []
    specialization: Optional[str] = None
    designation: Optional[str] = None
    affiliated_hospital: Optional[str] = None
    chamber_name: Optional[str] = None
    chamber_address: Optional[str] = None
    visiting_day: Optional[DAY] = None
    visiting_start_time: Optional[time] = None
    visiting_end_time: Optional[time] = None
