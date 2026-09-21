from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
from app.models.base import Base

class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    mdcn_number = Column(String, unique=True, index=True)
    specialty = Column(String, index=True)
    is_verified = Column(Boolean, default=False)
    location = Column(Geometry('POINT', srid=4326))
    bio = Column(String)

    # Relationships
    user = relationship("User", back_populates="doctor_profile")
    availability_slots = relationship("AvailabilitySlot", back_populates="doctor")
    appointments = relationship("Appointment", back_populates="doctor", foreign_keys="[Appointment.doctor_id]")
