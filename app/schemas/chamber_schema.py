from datetime import time
from typing import List, Optional

from models.doctor_chamber import DAY
from pydantic import BaseModel, ConfigDict


class VisitingHour(BaseModel):
    day: DAY
    start_time: Optional[time] = None
    end_time: Optional[time] = None

    model_config = ConfigDict(from_attributes=True)


class ChamberBase(BaseModel):
    chamber_name: str
    address: str
    longitude: Optional[float] = None
    latitude: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)


class ChamberRead(ChamberBase):
    id: int


class ChamberCreate(ChamberBase):
    pass


class ChamberUpdate(BaseModel):
    chamber_name: Optional[str] = None
    address: Optional[str] = None
    longitude: Optional[float] = None
    latitude: Optional[float] = None


class DoctorChamberRead(ChamberBase):
    contact_number: Optional[str] = None
    visiting_hours: Optional[List[VisitingHour]] = []
