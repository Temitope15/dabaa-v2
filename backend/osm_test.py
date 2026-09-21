import requests
import math

def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(dlon/2) * math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

def get_hospitals(lat, lng, radius=5000):
    overpass_url = "http://overpass-api.de/api/interpreter"
    overpass_query = f"""
    [out:json];
    (
      node["amenity"="hospital"](around:{radius},{lat},{lng});
      way["amenity"="hospital"](around:{radius},{lat},{lng});
    );
    out center;
    """
    response = requests.get(overpass_url, params={'data': overpass_query}, headers={'User-Agent': 'DaabaMedicalTriage/1.0'})
    data = response.json()
    
    hospitals = []
    for element in data['elements']:
        name = element.get('tags', {}).get('name')
        if not name:
            continue
            
        if element['type'] == 'node':
            h_lat = element['lat']
            h_lng = element['lon']
        else:
            h_lat = element.get('center', {}).get('lat')
            h_lng = element.get('center', {}).get('lon')
            
        if h_lat and h_lng:
            dist = haversine(lat, lng, h_lat, h_lng)
            hospitals.append({
                "id": f"osm-{element['id']}",
                "name": name, 
                "specialty": "General Hospital",
                "bio": "Nearby public/private healthcare facility.",
                "lat": h_lat, 
                "lng": h_lng,
                "distance_km": round(dist, 2)
            })
            
    # Sort by distance
    hospitals.sort(key=lambda x: x['distance_km'])
    return hospitals[:5]

print(get_hospitals(6.5244, 3.3792))
