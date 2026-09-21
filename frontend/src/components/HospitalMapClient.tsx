'use client';

import { useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
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

interface HospitalMapProps {
  doctors: Doctor[];
  userLat?: number;
  userLng?: number;
}

// Custom hook to fit bounds
function FitBounds({ markers }: { markers: [number, number][] }) {
  const map = useMap();
  useEffect(() => {
    if (markers.length > 0) {
      const bounds = L.latLngBounds(markers);
      map.fitBounds(bounds, { padding: [50, 50], maxZoom: 15 });
    }
  }, [map, markers]);
  return null;
}

export default function HospitalMapClient({ doctors, userLat = 6.5244, userLng = 3.3792 }: HospitalMapProps) {
  const markers: [number, number][] = doctors
    .filter(doc => doc.lat && doc.lng)
    .map(doc => [doc.lat!, doc.lng!]);

  if (userLat && userLng) {
    markers.push([userLat, userLng]);
  }

  return (
    <div className="h-[400px] w-full rounded-xl overflow-hidden border border-slate-200 shadow-sm relative z-0">
      <MapContainer 
        center={[userLat, userLng]} 
        zoom={12} 
        scrollWheelZoom={false}
        className="h-full w-full"
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        
        {/* User Location */}
        {userLat && userLng && (
          <Marker position={[userLat, userLng]}>
            <Popup>
              <strong>You are here</strong>
            </Popup>
          </Marker>
        )}

        {/* Doctor/Hospital Locations */}
        {doctors.map(doc => {
          if (!doc.lat || !doc.lng) return null;
          return (
            <Marker key={doc.id} position={[doc.lat, doc.lng]}>
              <Popup>
                <div className="p-1">
                  <strong className="block text-slate-900 mb-1">{doc.name}</strong>
                  <span className="text-xs text-blue-600 block mb-2">{doc.specialty}</span>
                  <p className="text-xs text-slate-500 mb-3">{doc.distance_km}km away</p>
                  <button 
                    onClick={() => {
                      // Trigger booking using the API
                      import('@/lib/api').then(({ bookAppointment }) => {
                        bookAppointment(doc.id).then((res) => {
                          alert(res.message || `Successfully booked appointment with ${doc.name}!`);
                        }).catch(e => {
                          alert(`Error booking appointment: ${e.message}`);
                        });
                      });
                    }}
                    className="w-full bg-blue-600 text-white text-xs font-medium py-1.5 rounded hover:bg-blue-700 mt-2"
                  >
                    {doc.is_hospital ? "Get Directions" : "Book Appointment"}
                  </button>
                </div>
              </Popup>
            </Marker>
          );
        })}

        <FitBounds markers={markers} />
      </MapContainer>

      {/* AI Recommendation Overlay */}
      {doctors.length > 0 && (
        <div className="absolute top-4 right-4 z-[1000] bg-white p-4 rounded-xl shadow-lg border border-blue-100 max-w-xs animate-in slide-in-from-right-8 fade-in">
          <div className="flex gap-3 mb-2">
            <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center text-white font-bold text-xs shrink-0">
              D
            </div>
            <p className="text-sm text-slate-800 font-medium leading-snug">
              {doctors[0].is_hospital ? (
                <>I recommend proceeding to <span className="font-bold text-blue-600">{doctors[0].name}</span> as a walk-in patient because they are the closest healthcare facility to you ({doctors[0].distance_km}km).</>
              ) : (
                <>I recommend <span className="font-bold text-blue-600">{doctors[0].name}</span> because they specialize in <span className="font-bold">{doctors[0].specialty}</span> and are closest to you ({doctors[0].distance_km}km).</>
              )}
            </p>
          </div>
          <button 
            onClick={() => {
              import('@/lib/api').then(({ bookAppointment }) => {
                bookAppointment(doctors[0].id).then((res) => {
                  alert(res.message || `Successfully booked appointment with ${doctors[0].name}!`);
                }).catch(e => alert(`Error booking appointment: ${e.message}`));
              });
            }}
            className="w-full bg-blue-600 text-white text-sm font-medium py-2 rounded-lg hover:bg-blue-700 mt-2 transition-colors"
          >
            {doctors[0].is_hospital ? "Get Directions" : "Book Appointment Now"}
          </button>
        </div>
      )}
    </div>
  );
}
