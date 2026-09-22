from typing import List, Dict, Any
from app.core.database import SessionLocal
from app.models.doctor import Doctor
from sqlalchemy import text

class ReferralAgent:
    def __init__(self):
        pass
        
    def find_doctors(self, specialty: str, patient_lat: float, patient_lng: float, radius_km: int = 50) -> List[Dict[str, Any]]:
        db = SessionLocal()
        try:
            # We use ST_DWithin to find doctors within the given radius in kilometers
            # Geography cast automatically calculates in meters
            query = text("""
                SELECT d.id, u.full_name, d.specialty, d.bio, 
                       ST_Y(d.location::geometry) AS lat, 
                       ST_X(d.location::geometry) AS lng,
                       ST_Distance(d.location::geography, ST_SetSRID(ST_MakePoint(:lng, :lat), 4326)::geography) / 1000.0 AS distance_km
                FROM doctors d
                JOIN users u ON d.user_id = u.id
                WHERE d.is_verified = True 
                  AND d.specialty = :specialty
                  AND ST_DWithin(d.location::geography, ST_SetSRID(ST_MakePoint(:lng, :lat), 4326)::geography, :radius_meters)
                ORDER BY distance_km ASC
                LIMIT 5
            """)
            
            result = db.execute(query, {
                "specialty": specialty,
                "lat": patient_lat,
                "lng": patient_lng,
                "radius_meters": radius_km * 1000
            })
            
            doctors = []
            for row in result:
                doctors.append({
                    "id": row.id,
                    "name": row.full_name,
                    "specialty": row.specialty,
                    "bio": row.bio,
                    "lat": float(row.lat),
                    "lng": float(row.lng),
                    "distance_km": round(row.distance_km, 2),
                    "is_hospital": False
                })
                
            if not doctors:
                return self.get_fallback_hospitals(patient_lat, patient_lng, radius_km)
                
            return doctors
        finally:
            db.close()

    def get_fallback_hospitals(self, lat: float, lng: float, radius_km: int = 5) -> List[Dict[str, Any]]:
        # Instantly return fallback hospitals for prototype speed
        return [
            {
                "id": "mock-hospital-1",
                "name": "Lagos University Teaching Hospital (LUTH)",
                "specialty": "General Hospital",
                "bio": "Premier public healthcare facility with comprehensive emergency and specialized care.",
                "lat": 6.5222,
                "lng": 3.3500,
                "distance_km": 3.2,
                "is_hospital": True
            },
            {
                "id": "mock-hospital-2",
                "name": "Federal Medical Centre (FMC)",
                "specialty": "Emergency Care",
                "bio": "Top-tier federal facility equipped for trauma and surgical emergencies.",
                "lat": 6.4950,
                "lng": 3.3710,
                "distance_km": 4.1,
                "is_hospital": True
            }
        ]

referral_agent = ReferralAgent()
