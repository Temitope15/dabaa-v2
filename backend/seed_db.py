import os
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine
from app.models.base import Base
from app.models.user import User
from app.models.doctor import Doctor
from app.models.appointment import AvailabilitySlot, Appointment
from datetime import datetime, timedelta, timezone

def seed_database():
    db: Session = SessionLocal()

    print("Seeding database...")
    
    # Check if a user already exists
    existing_user = db.query(User).filter(User.email == "patient@daaba.com").first()
    if not existing_user:
        patient = User(
            full_name="John Doe",
            phone_number="+2348000000000",
            email="patient@daaba.com",
            hashed_password="hashed_password",
            date_of_birth=datetime(1990, 1, 1).date()
        )
        db.add(patient)
        
        doctor_user = User(
            full_name="Dr. Jane Smith",
            phone_number="+2348000000001",
            email="doctor@daaba.com",
            hashed_password="hashed_password"
        )
        db.add(doctor_user)
        db.commit()
        db.refresh(patient)
        db.refresh(doctor_user)

        doctor = Doctor(
            user_id=doctor_user.id,
            mdcn_number="MDCN123456",
            specialty="Cardiologist",
            is_verified=True,
            location="SRID=4326;POINT(3.3792 6.5244)",
            bio="Experienced Cardiologist in Lagos."
        )
        db.add(doctor)
        db.commit()
        db.refresh(doctor)

        slot = AvailabilitySlot(
            doctor_id=doctor.id,
            start_time=datetime.now(timezone.utc) + timedelta(days=1),
            end_time=datetime.now(timezone.utc) + timedelta(days=1, hours=1),
            is_booked=True
        )
        db.add(slot)
        db.commit()
        db.refresh(slot)

        appointment = Appointment(
            patient_id=patient.id,
            doctor_id=doctor.id,
            slot_id=slot.id,
            status="Confirmed",
            ai_symptoms_summary="Patient reported mild chest pain and shortness of breath."
        )
        db.add(appointment)
        db.commit()
        
        print("Database seeded successfully with test data.")
    else:
        print("Data already exists in the database. Seed skipped.")

    db.close()

if __name__ == "__main__":
    seed_database()
