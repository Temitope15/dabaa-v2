'use client';

import { useEffect, useState } from 'react';
import { api } from '@/lib/api';

type Appointment = {
  id: string;
  patient_name: string;
  symptoms_summary: string;
  status: string;
};

export default function DoctorAppointmentsPage() {
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const fetchAppointments = async () => {
    setIsLoading(true);
    try {
      const res = await api.get('/doctor/appointments');
      setAppointments(res.data);
    } catch (err) {
      console.error('Failed to fetch appointments', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchAppointments();
  }, []);

  const handleAction = async (id: string, action: 'accept' | 'reject') => {
    try {
      await api.put(`/doctor/appointments/${id}/${action}`);
      fetchAppointments();
    } catch (err) {
      console.error(`Failed to ${action} appointment`, err);
    }
  };

  return (
    <div className="flex-1 overflow-y-auto p-8">
      <div className="max-w-4xl mx-auto space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Appointment Requests</h1>
          <p className="mt-2 text-slate-600">Manage your upcoming patient appointments.</p>
        </div>

        {isLoading ? (
          <div>Loading appointments...</div>
        ) : appointments.length === 0 ? (
          <div className="bg-white p-8 text-center rounded-2xl border border-slate-200">
            <p className="text-slate-500">No appointments found.</p>
          </div>
        ) : (
          <div className="space-y-4">
            {appointments.map((appointment) => (
              <div key={appointment.id} className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 flex flex-col sm:flex-row gap-4 justify-between items-start sm:items-center">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="text-lg font-semibold text-slate-900">{appointment.patient_name}</h3>
                    <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      appointment.status === 'Pending' ? 'bg-yellow-100 text-yellow-800' :
                      appointment.status === 'Confirmed' ? 'bg-green-100 text-green-800' :
                      'bg-red-100 text-red-800'
                    }`}>
                      {appointment.status}
                    </span>
                  </div>
                  <p className="text-sm text-slate-600">
                    <span className="font-medium">Symptoms Summary:</span> {appointment.symptoms_summary}
                  </p>
                </div>
                
                {appointment.status === 'Pending' && (
                  <div className="flex gap-2 w-full sm:w-auto">
                    <button
                      onClick={() => handleAction(appointment.id, 'accept')}
                      className="flex-1 sm:flex-none px-4 py-2 bg-green-600 text-white rounded-md text-sm font-medium hover:bg-green-700 transition-colors"
                    >
                      Accept
                    </button>
                    <button
                      onClick={() => handleAction(appointment.id, 'reject')}
                      className="flex-1 sm:flex-none px-4 py-2 bg-red-600 text-white rounded-md text-sm font-medium hover:bg-red-700 transition-colors"
                    >
                      Reject
                    </button>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
