from pydantic import BaseModel, Field
from enum import Enum
from typing import List, Optional

class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    EMERGENCY = "EMERGENCY"

class Location(BaseModel):
    lat: float
    lng: float

class PatientState(BaseModel):
    patient_id: int
    current_symptoms: List[str] = Field(default_factory=list)
    risk_level: Optional[RiskLevel] = None
    location: Optional[Location] = None
    required_specialty: Optional[str] = None
