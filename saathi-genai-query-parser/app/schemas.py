from pydantic import BaseModel
from typing import Optional
from datetime import date

class VisaQuery(BaseModel):
    destination: str
    passport_country: str
    travel_date: date
    purpose: str

class VisaRequirementsResponse(BaseModel):
    country: str
    requirements: str
    processing_time: Optional[str] = None
    additional_notes: Optional[str] = None