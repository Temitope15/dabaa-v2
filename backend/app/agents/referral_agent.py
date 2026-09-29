import httpx
import math
from typing import List, Dict, Any

class ReferralAgent:
    def __init__(self):
        self.overpass_url = "https://overpass-api.de/api/interpreter"
        self.nominatim_url = "https://nominatim.openstreetmap.org/reverse"
        self.headers = {"User-Agent": "Daaba-Triage/1.0"}

    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate the great circle distance between two points on the earth (specified in decimal degrees)."""
        # Convert decimal degrees to radians
        lon1, lat1, lon2, lat2 = map(math.radians, [lon1, lat1, lon2, lat2])
        # Haversine formula
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.asin(math.sqrt(a))
        r = 6371  # Radius of earth in kilometers
        return round(c * r, 2)

    def _query_overpass(self, query: str) -> List[Dict[str, Any]]:
        """Execute a query against the Overpass API."""
        try:
            with httpx.Client(timeout=15.0) as client:
                response = client.get(self.overpass_url, params={'data': query}, headers=self.headers)
                response.raise_for_status()
                data = response.json()
                return data.get('elements', [])
        except Exception as e:
            print(f"Overpass API error: {e}")
            return []

    def _parse_elements(self, elements: List[Dict], patient_lat: float, patient_lng: float) -> List[Dict]:
        """Parse OSM elements into the format expected by the frontend."""
        results = []
        for el in elements:
            if 'tags' in el and 'name' in el['tags']:
                name = el['tags']['name']
                # Node has lat/lon directly, way/relation has it in center
                lat = el.get('lat', el.get('center', {}).get('lat'))
                lng = el.get('lon', el.get('center', {}).get('lon'))
                
                if lat and lng:
                    dist = self._calculate_distance(patient_lat, patient_lng, lat, lng)
                    # Use OSM id as a string id for booking/map selection
                    is_hospital = el['tags'].get('amenity') == 'hospital'
                    
                    # Generate a mock bio based on tags
                    speciality = el['tags'].get('healthcare:speciality', 'General Medical Facility').title()
                    phone = el['tags'].get('phone', 'No phone listed')
                    bio = f"Facility type: {el['tags'].get('amenity', 'healthcare').title()}. Phone: {phone}"
                    
                    results.append({
                        "id": f"osm-{el['id']}",
                        "name": name,
                        "specialty": speciality,
                        "bio": bio,
                        "lat": float(lat),
                        "lng": float(lng),
                        "distance_km": dist,
                        "is_hospital": is_hospital
                    })
        
        # Sort by distance and return top 5
        results.sort(key=lambda x: x['distance_km'])
        return results[:5]

    def _map_specialty_to_osm_tag(self, specialty: str) -> str:
        """Map common medical specialties to OSM healthcare:speciality tags."""
        s = specialty.lower()
        if "cardio" in s: return "cardiology"
        if "neuro" in s: return "neurology"
        if "pedia" in s: return "paediatrics"
        if "derma" in s: return "dermatology"
        if "psych" in s: return "psychiatry"
        if "ortho" in s: return "orthopaedics"
        if "gyn" in s: return "gynaecology"
        if "ophth" in s: return "ophthalmology"
        if "ent" in s: return "otolaryngology"
        return ""

    def find_doctors(self, specialty: str, patient_lat: float, patient_lng: float) -> tuple[List[Dict[str, Any]], str]:
        """
        Intelligently route patients to doctors/hospitals based on location.
        Returns: (List of doctors/hospitals, Warning/Info Message)
        """
        # Step 1: Try finding the specific specialist within 20km
        osm_specialty = self._map_specialty_to_osm_tag(specialty)
        if osm_specialty:
            query = f"""
            [out:json];
            (
              node["healthcare:speciality"~"{osm_specialty}"](around:20000,{patient_lat},{patient_lng});
              way["healthcare:speciality"~"{osm_specialty}"](around:20000,{patient_lat},{patient_lng});
            );
            out center;
            """
            elements = self._query_overpass(query)
            specialists = self._parse_elements(elements, patient_lat, patient_lng)
            if specialists:
                return specialists, ""

        # Step 2: Fallback to general hospitals/clinics within 15km
        query_local = f"""
        [out:json];
        (
          node["amenity"~"hospital|clinic"](around:15000,{patient_lat},{patient_lng});
          way["amenity"~"hospital|clinic"](around:15000,{patient_lat},{patient_lng});
        );
        out center;
        """
        elements = self._query_overpass(query_local)
        hospitals = self._parse_elements(elements, patient_lat, patient_lng)
        if hospitals:
            msg = f"We couldn't find a specific {specialty} nearby, but we found these local hospitals based on your location."
            return hospitals, msg

        # Step 3: Expand search to 50km if rural
        query_expanded = f"""
        [out:json];
        (
          node["amenity"~"hospital|clinic"](around:50000,{patient_lat},{patient_lng});
          way["amenity"~"hospital|clinic"](around:50000,{patient_lat},{patient_lng});
        );
        out center;
        """
        elements = self._query_overpass(query_expanded)
        hospitals = self._parse_elements(elements, patient_lat, patient_lng)
        
        if hospitals:
            msg = f"There are no hospitals in your immediate region. We found these facilities further away; you may have to travel."
            return hospitals, msg
            
        # Absolute fallback if even 50km fails
        return [], "We couldn't find any medical facilities in your extended area. Please contact local emergency services immediately."

referral_agent = ReferralAgent()
