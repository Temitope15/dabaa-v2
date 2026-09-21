from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from app.models.base import Base

class AvailabilitySlot(Base):
    __tablename__ = "availability_slots"

    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey("doctors.id"))
    start_time = Column(DateTime(timezone=True), index=True)
    end_time = Column(DateTime(timezone=True))
    is_booked = Column(Boolean, default=False)

    # Relationships
    doctor = relationship("Doctor", back_populates="availability_slots")
    appointment = relationship("Appointment", back_populates="slot", uselist=False)

class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("users.id"))
    doctor_id = Column(Integer, ForeignKey("doctors.id"))
    slot_id = Column(Integer, ForeignKey("availability_slots.id"), unique=True)
    status = Column(String, default="Pending") # Pending, Confirmed, Cancelled, Completed
    ai_symptoms_summary = Column(Text, nullable=True)

    # Relationships
    patient = relationship("User", back_populates="appointments", foreign_keys=[patient_id])
    doctor = relationship("Doctor", back_populates="appointments", foreign_keys=[doctor_id])
    slot = relationship("AvailabilitySlot", back_populates="appointment")
