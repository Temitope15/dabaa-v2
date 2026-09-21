from app.schemas.patient_state import PatientState, RiskLevel, Location
from app.schemas.agent_actions import TriageResult, ReferralRequest
from pydantic import ValidationError

def run_tests():
    print("Testing Pydantic Schemas...")

    # Test 1: Valid Patient State
    try:
        state = PatientState(
            patient_id=1,
            current_symptoms=["headache", "fever"],
            risk_level=RiskLevel.MEDIUM,
            location=Location(lat=6.524, lng=3.379)
        )
        print("✅ Valid PatientState created.")
    except ValidationError as e:
        print(f"❌ Failed to create valid PatientState: {e}")

    # Test 2: Invalid Risk Level (should fail)
    try:
        invalid_state = PatientState(
            patient_id=2,
            risk_level="KINDA_SICK" # This should throw an error
        )
        print("❌ Invalid PatientState should have failed, but didn't.")
    except ValidationError as e:
        print("✅ Successfully caught invalid risk_level: 'KINDA_SICK'")

    # Test 3: Triage Result
    try:
        triage = TriageResult(
            symptoms_summary="Patient has persistent headache and fever of 39C.",
            recommended_specialty="General Practitioner",
            is_emergency=False
        )
        print("✅ Valid TriageResult created.")
    except ValidationError as e:
        print(f"❌ Failed to create valid TriageResult: {e}")

    # Test 4: Referral Request
    try:
        referral = ReferralRequest(
            specialty="Cardiologist",
            max_distance_km=15.5
        )
        print("✅ Valid ReferralRequest created.")
    except ValidationError as e:
        print(f"❌ Failed to create valid ReferralRequest: {e}")

if __name__ == "__main__":
    run_tests()
