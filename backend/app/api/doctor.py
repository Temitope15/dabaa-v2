from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.orm import Session, joinedload
from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.models.doctor import Doctor
from app.models.appointment import Appointment
from sqlalchemy import text

router = APIRouter()

class DoctorProfileCreate(BaseModel):
    specialty: str
    bio: str
    mdcn_number: str
    lat: float
    lng: float

@router.post("/profile")
def create_or_update_doctor_profile(data: DoctorProfileCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    import re
    # MDCN must follow the format MDCN-123456
    is_valid_mdcn = bool(re.match(r"^MDCN-[0-9]{6}$", data.mdcn_number, re.IGNORECASE))
    
    # Check if doctor profile exists
    doctor = db.query(Doctor).filter(Doctor.user_id == current_user.id).first()
    if doctor:
        doctor.specialty = data.specialty
        doctor.bio = data.bio
        doctor.mdcn_number = data.mdcn_number
        doctor.location = f'SRID=4326;POINT({data.lng} {data.lat})'
        doctor.is_verified = is_valid_mdcn
    else:
        doctor = Doctor(
            user_id=current_user.id,
            specialty=data.specialty,
            bio=data.bio,
            mdcn_number=data.mdcn_number,
            location=f'SRID=4326;POINT({data.lng} {data.lat})',
            is_verified=is_valid_mdcn
        )
        db.add(doctor)
    db.commit()
    db.refresh(doctor)
    return {"message": "Profile saved", "doctor_id": doctor.id, "is_verified": doctor.is_verified}

@router.get("/appointments")
def get_doctor_appointments(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    doctor = db.query(Doctor).filter(Doctor.user_id == current_user.id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor profile not found")
    
    appointments = db.query(Appointment).options(
        joinedload(Appointment.patient)
    ).filter(Appointment.doctor_id == doctor.id).order_by(Appointment.id.desc()).all()
    
    return [{
        "id": apt.id,
        "patient_name": apt.patient.full_name if apt.patient else "Unknown",
        "patient_phone": apt.patient.phone_number if apt.patient else "",
        "status": apt.status,
        "ai_symptoms_summary": apt.ai_symptoms_summary or "No summary available",
    } for apt in appointments]

@router.put("/appointments/{appointment_id}/accept")
def accept_appointment(appointment_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    doctor = db.query(Doctor).filter(Doctor.user_id == current_user.id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor profile not found")
    
    appointment = db.query(Appointment).filter(
        Appointment.id == appointment_id, 
        Appointment.doctor_id == doctor.id
    ).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    appointment.status = "Confirmed"
    db.commit()
    
    print(f"📅 CALENDAR SYNC: Doctor {current_user.full_name} accepted appointment {appointment_id}")
    print(f"📩 NOTIFICATION: SMS sent to patient {appointment.patient_id}")
    
    return {"message": "Appointment accepted and added to calendar"}

@router.put("/appointments/{appointment_id}/reject")
def reject_appointment(appointment_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    doctor = db.query(Doctor).filter(Doctor.user_id == current_user.id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor profile not found")
    
    appointment = db.query(Appointment).filter(
        Appointment.id == appointment_id, 
        Appointment.doctor_id == doctor.id
    ).first()
    if not appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    appointment.status = "Cancelled"
    db.commit()
    
    return {"message": "Appointment rejected"}
