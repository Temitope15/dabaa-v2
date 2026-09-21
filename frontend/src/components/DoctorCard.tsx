import React, { useState } from 'react';
import { Doctor, bookAppointment } from '../lib/api';

interface DoctorCardProps {
  doctor: Doctor;
}

export function DoctorCard({ doctor }: DoctorCardProps) {
  const [isBooking, setIsBooking] = useState(false);
  const [isBooked, setIsBooked] = useState(false);
  
  const handleBook = async () => {
    setIsBooking(true);
    try {
      await bookAppointment(doctor.id);
      setIsBooked(true);
    } catch (e) {
      alert("Failed to book appointment.");
    } finally {
      setIsBooking(false);
    }
  };

  return (
    <div className="bg-white border border-slate-200 rounded-xl p-4 shadow-sm my-2 max-w-sm w-full">
      <div className="flex items-start justify-between">
        <div>
          <h3 className="font-semibold text-slate-800 text-lg">{doctor.name}</h3>
          <p className="text-blue-600 text-sm font-medium">{doctor.specialty}</p>
        </div>
        <div className="bg-slate-100 px-2 py-1 rounded-md text-xs font-semibold text-slate-600">
          {doctor.distance_km} km
        </div>
      </div>
      <p className="text-slate-500 text-sm mt-3 leading-relaxed">
        {doctor.bio}
      </p>
      <button 
        onClick={handleBook}
        disabled={isBooking || isBooked}
        className={`mt-4 w-full font-medium py-2 rounded-lg transition-colors text-sm ${
          isBooked ? 'bg-green-100 text-green-700' : 
          'bg-blue-600 hover:bg-blue-700 text-white disabled:bg-blue-400'
        }`}
      >
        {isBooking ? 'Booking...' : isBooked ? 'Appointment Booked!' : 'Book Appointment'}
      </button>
    </div>
  );
}
