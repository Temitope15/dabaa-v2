'use client';

import { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap, Polyline } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import { Doctor } from '@/lib/api';

// Fix Leaflet's default icon path issues in Next.js
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
});

// Custom Icons
const UserIcon = new L.Icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-blue.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});

const HospitalIcon = new L.Icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});

interface RideMapProps {
  doctors: Doctor[];
  userLat?: number;
  userLng?: number;
  selectedDoctorId?: string | number | null;
  onDoctorSelect: (id: string | number) => void;
}

// Component to handle dynamic map bounds and routing
function MapController({ 
  userLat, 
  userLng, 
  targetDoc,
  setRouteCoords
}: { 
  userLat: number, 
  userLng: number, 
  targetDoc?: Doctor,
  setRouteCoords: (coords: [number, number][]) => void
}) {
  const map = useMap();

  useEffect(() => {
    if (!targetDoc?.lat || !targetDoc?.lng) {
      // Just center on user if no target
      map.flyTo([userLat, userLng], 14);
      setRouteCoords([]);
      return;
    }

    // We have a target, fetch route from OSRM
    const fetchRoute = async () => {
      try {
        // OSRM expects lon,lat
        const url = `https://router.project-osrm.org/route/v1/driving/${userLng},${userLat};${targetDoc.lng},${targetDoc.lat}?overview=full&geometries=geojson`;
        const res = await fetch(url);
        const data = await res.json();
        
        if (data.routes && data.routes[0]) {
          // OSRM returns GeoJSON coordinates as [lon, lat]
          const coords = data.routes[0].geometry.coordinates.map((c: [number, number]) => [c[1], c[0]]);
          setRouteCoords(coords);
          
          // Fit bounds to the route
          const bounds = L.latLngBounds(coords);
          map.fitBounds(bounds, { padding: [50, 50], maxZoom: 16 });
        }
      } catch (err) {
        console.error("Failed to fetch route:", err);
        // Fallback to just framing the two points
        const bounds = L.latLngBounds([[userLat, userLng], [targetDoc.lat!, targetDoc.lng!]]);
        map.fitBounds(bounds, { padding: [50, 50], maxZoom: 16 });
      }
    };

    fetchRoute();
  }, [map, userLat, userLng, targetDoc, setRouteCoords]);

  return null;
}

export default function RideMapClient({ 
  doctors, 
  userLat = 6.5244, 
  userLng = 3.3792,
  selectedDoctorId,
  onDoctorSelect
}: RideMapProps) {
  const [routeCoords, setRouteCoords] = useState<[number, number][]>([]);
  const selectedDoc = doctors.find(d => d.id === selectedDoctorId);

  return (
    <div className="absolute inset-0 w-full h-full z-0">
      <MapContainer 
        center={[userLat, userLng]} 
        zoom={13} 
        scrollWheelZoom={true}
        zoomControl={false}
        className="w-full h-full"
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png"
        />
        
        {/* User Location */}
        <Marker position={[userLat, userLng]} icon={UserIcon}>
          <Popup>You are here</Popup>
        </Marker>

        {/* Route Polyline */}
        {routeCoords.length > 0 && (
          <Polyline 
            positions={routeCoords} 
            color="#2563eb" 
            weight={4} 
            opacity={0.8}
            dashArray="10, 10"
            lineCap="round"
          />
        )}

        {/* Doctor/Hospital Locations */}
        {doctors.map(doc => {
          if (!doc.lat || !doc.lng) return null;
          const isSelected = selectedDoc?.id === doc.id;
          
          return (
            <Marker 
              key={doc.id} 
              position={[doc.lat, doc.lng]} 
              icon={HospitalIcon}
              eventHandlers={{
                click: () => onDoctorSelect(doc.id)
              }}
            >
              {isSelected && (
                <Popup>
                  <div className="font-bold">{doc.name}</div>
                  <div className="text-xs text-slate-500">{doc.distance_km}km away</div>
                </Popup>
              )}
            </Marker>
          );
        })}

        <MapController 
          userLat={userLat} 
          userLng={userLng} 
          targetDoc={selectedDoc}
          setRouteCoords={setRouteCoords}
        />
      </MapContainer>
    </div>
  );
}
