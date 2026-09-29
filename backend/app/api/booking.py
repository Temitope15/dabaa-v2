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
    hospital_name: str | None = None
    lat: float | None = None
    lng: float | None = None

@router.post("/book")
async def book_appointment(request: BookingRequest, current_user: User = Depends(get_current_user)):
    db = SessionLocal()
    try:
        # Check if it's a fallback OSM or mock hospital
        if isinstance(request.doctor_id, str) and not request.doctor_id.isdigit():
            print("\n" + "="*50)
            print(f"🗺️ EXTERNAL ROUTING: Directions/Booking requested for hospital {request.hospital_name}!")
            print(f"📩 NOTIFICATION AGENT: Sent SMS to Patient {current_user.id} with hospital location details.")
            print("="*50 + "\n")
            
            appointment = Appointment(
                patient_id=current_user.id,
                doctor_id=None,
                external_hospital_name=request.hospital_name or request.doctor_id,
                external_lat=request.lat,
                external_lng=request.lng,
                status="Routing",
                ai_symptoms_summary="Triage confirmed. User routing to external hospital."
            )
            db.add(appointment)
            db.commit()
            return {"message": "Booking saved! You are now being routed.", "is_external": True, "lat": request.lat, "lng": request.lng}

        # Regular Doctor Booking
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
        
        return {"message": "Appointment successfully booked and calendar updated.", "is_external": False}
    except Exception as e:
        import traceback
        traceback.print_exc()
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()

@router.get("/appointments/me")
async def get_my_appointments(current_user: User = Depends(get_current_user)):
    db = SessionLocal()
    try:
        from sqlalchemy.orm import joinedload
        appointments = db.query(Appointment).options(
            joinedload(Appointment.doctor)
        ).filter(Appointment.patient_id == current_user.id).all()
        
        return [
            {
                "id": a.id,
                "status": a.status,
                "ai_symptoms_summary": a.ai_symptoms_summary,
                "doctor_name": a.external_hospital_name if a.external_hospital_name else (a.doctor.user.full_name if a.doctor else "Unknown Doctor"),
                "doctor_specialty": "External Routing" if a.external_hospital_name else (a.doctor.specialty if a.doctor else "Unknown"),
                "date": "TBD" # Replace with actual slot date when implemented
            }
            for a in appointments
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        db.close()
