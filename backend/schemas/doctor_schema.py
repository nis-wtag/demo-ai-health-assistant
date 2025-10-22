from datetime import time
from typing import List, Optional

from models.doctor_chamber import DAY
from pydantic import BaseModel, ConfigDict, Field

from schemas.chamber_schema import ChamberUpdate, DoctorChamberRead


class DoctorBase(BaseModel):
    full_name: str
    image: Optional[str] = None
    degrees: List[str] = Field(default_factory=list)
    specialization: Optional[str] = None
    designation: Optional[str] = None
    affiliated_hospital: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class DoctorCreate(DoctorBase):
    chambers: List[DoctorChamberRead] = Field(default_factory=list)


class DoctorUpdate(BaseModel):
    image: Optional[str] = None
    full_name: Optional[str]
    degrees: Optional[List[str]] = Field(default_factory=list)
    specialization: Optional[str] = None
    designation: Optional[str] = None
    affiliated_hospital: Optional[str] = None
    chambers: Optional[List[ChamberUpdate]] = Field(default_factory=list)


class DoctorRead(DoctorBase):
    id: int
    chambers: List[DoctorChamberRead] = Field(default_factory=list)

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
