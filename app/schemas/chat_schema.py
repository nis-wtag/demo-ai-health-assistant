from typing import Optional

from pydantic import BaseModel

from schemas.doctor_schema import DoctorRead


class ChatQuery(BaseModel):
    query: str


class ChatResponse(BaseModel):
    disclaimer: str
    remedy: str
    recommended_doctors: Optional[list[DoctorRead]] = []
