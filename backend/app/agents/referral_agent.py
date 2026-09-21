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
        import requests
        import math
        
        def haversine(lat1, lon1, lat2, lon2):
            R = 6371
            dlat = math.radians(lat2 - lat1)
            dlon = math.radians(lon2 - lon1)
            a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
            return R * c

        try:
            overpass_url = "http://overpass-api.de/api/interpreter"
            radius_m = radius_km * 1000
            overpass_query = f"[out:json];(node['amenity'='hospital'](around:{radius_m},{lat},{lng});way['amenity'='hospital'](around:{radius_m},{lat},{lng}););out center;"
            response = requests.get(overpass_url, params={'data': overpass_query}, headers={'User-Agent': 'DaabaMedicalTriage/1.0'}, timeout=5)
            data = response.json()
            
            hospitals = []
            for el in data.get('elements', []):
                name = el.get('tags', {}).get('name')
                if not name: continue
                
                h_lat = el['lat'] if el['type'] == 'node' else el.get('center', {}).get('lat')
                h_lng = el['lon'] if el['type'] == 'node' else el.get('center', {}).get('lon')
                
                if h_lat and h_lng:
                    dist = haversine(lat, lng, h_lat, h_lng)
                    hospitals.append({
                        "id": f"osm-{el['id']}",
                        "name": name,
                        "specialty": "General Hospital",
                        "bio": "Nearby public/private healthcare facility.",
                        "lat": h_lat,
                        "lng": h_lng,
                        "distance_km": round(dist, 2),
                        "is_hospital": True
                    })
            hospitals.sort(key=lambda x: x['distance_km'])
            
            if not hospitals:
                raise Exception("OSM returned empty list")
                
            return hospitals[:5]
        except Exception as e:
            print(f"OSM Fallback failed: {e}")
            # Guaranteed Mock Fallback for Prototype
            return [{
                "id": "mock-hospital-1",
                "name": "Lagos University Teaching Hospital (LUTH)",
                "specialty": "General Hospital",
                "bio": "Premier public healthcare facility with comprehensive emergency and specialized care.",
                "lat": 6.5222,
                "lng": 3.3500,
                "distance_km": 3.2,
                "is_hospital": True
            }]

referral_agent = ReferralAgent()
