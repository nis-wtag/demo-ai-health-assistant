from pydantic import BaseModel


class DashboardStats(BaseModel):
    doctor_count: int
    chamber_count: int
