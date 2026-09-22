from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.core.database import SessionLocal
from app.models.appointment import Appointment
from app.api.deps import get_current_user
from app.models.user import User
import datetime

router = APIRouter()

class BookingRequest(BaseModel):
    doctor_id: str | int

@router.post("/book")
async def book_appointment(request: BookingRequest, current_user: User = Depends(get_current_user)):
    db = SessionLocal()
    try:
        # Check if it's a fallback OSM or mock hospital
        # Any doctor_id that isn't purely numeric should be treated as a hospital/external routing
        if isinstance(request.doctor_id, str) and not request.doctor_id.isdigit():
            print("\n" + "="*50)
            print(f"🗺️ EXTERNAL ROUTING: Directions/Booking requested for hospital {request.doctor_id}!")
            print(f"📩 NOTIFICATION AGENT: Sent SMS to Patient {current_user.id} with hospital location details.")
            print("="*50 + "\n")
            return {"message": "Booking request sent! Please proceed to the hospital."}

        # In a real app, we'd assign a proper slot. We'll mock a generic confirmed appointment.
        appointment = Appointment(
            patient_id=current_user.id,
            doctor_id=int(request.doctor_id),
            status="Pending",
            ai_symptoms_summary="Triage confirmed via Daaba AI."
        )
        db.add(appointment)
        db.commit()
        db.refresh(appointment)
        
        # --- Mock Calendar & Notification Sync ---
        print("\n" + "="*50)
        print(f"🗓️ CALENDAR SYNC: Appointment {appointment.id} created!")
        print(f"📩 NOTIFICATION AGENT: Sent SMS to Patient {current_user.id} via Termii API.")
        print(f"📩 NOTIFICATION AGENT: Sent SMS to Doctor {request.doctor_id} via Termii API.")
        print("="*50 + "\n")
        
        return {"message": "Appointment successfully booked and calendar updated."}
    except Exception as e:
        import traceback
        traceback.print_exc()
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()
