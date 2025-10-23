from pydantic import BaseModel, Field
from schemas.doctor_schema import DoctorSearch


class StructuredAIResponse(BaseModel):
    remedy: str = Field(
        description="A safe, educational, non-prescriptive home remedy for the user's symptoms. This should be helpful even if no doctors are found."
    )
    search_parameters: DoctorSearch = Field(
        description="The structured search parameters extracted from the user's query to find a doctor."
    )
