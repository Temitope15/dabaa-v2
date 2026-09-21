from pydantic import BaseModel, Field

class TriageResult(BaseModel):
    symptoms_summary: str = Field(description="A concise medical summary of the patient's reported symptoms.")
    recommended_specialty: str = Field(description="The type of doctor recommended, e.g., 'General Practitioner', 'Cardiologist'.")
    is_emergency: bool = Field(description="True if the symptoms indicate a potential life-threatening emergency requiring immediate physical attention.")

class ReferralRequest(BaseModel):
    specialty: str = Field(description="The medical specialty of the doctor to search for.")
    max_distance_km: float = Field(default=10.0, description="The maximum distance in kilometers to search for a doctor.")
