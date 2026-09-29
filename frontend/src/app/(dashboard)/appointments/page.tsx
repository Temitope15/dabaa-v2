'use client';
import { useEffect, useState } from 'react';
import { api } from '@/lib/api';

interface Appointment {
  id: number;
  status: string;
  ai_symptoms_summary: string;
  doctor_name: string;
  doctor_specialty: string;
  date: string;
}

export default function AppointmentsPage() {
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAppointments = async () => {
      try {
        const res = await api.get('/appointments/me');
        setAppointments(res.data);
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    };
    fetchAppointments();
  }, []);

  return (
    <div className="flex flex-col h-full bg-slate-50 relative p-8">
      <div className="max-w-3xl mx-auto w-full mt-8">
        <h1 className="text-3xl font-bold text-slate-900 mb-6">Appointments</h1>
        
        {loading ? (
          <div className="text-center py-10">Loading appointments...</div>
        ) : appointments.length === 0 ? (
          <div className="bg-white rounded-2xl border border-slate-200 p-8 text-center shadow-sm">
            <div className="w-16 h-16 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center mx-auto mb-4 text-2xl font-bold">
              📅
            </div>
            <h2 className="text-xl font-semibold text-slate-800 mb-2">No Upcoming Appointments</h2>
            <p className="text-slate-500 mb-6">You don't have any appointments booked yet. Go to the Chat Triage to find a doctor.</p>
            <a href="/chat" className="bg-blue-600 text-white font-medium py-2 px-6 rounded-lg hover:bg-blue-700 transition-colors inline-block">
              Start Triage
            </a>
          </div>
        ) : (
          <div className="space-y-4">
            {appointments.map(app => (
              <div key={app.id} className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm flex items-center justify-between">
                <div>
                  <h3 className="font-bold text-lg text-slate-800">
                    {app.doctor_specialty === 'External Routing' ? app.doctor_name : `Dr. ${app.doctor_name}`}
                  </h3>
                  <p className="text-slate-500 text-sm">{app.doctor_specialty}</p>
                  <p className="text-sm mt-2 text-slate-600 font-medium">Triage Summary:</p>
                  <p className="text-sm text-slate-500 line-clamp-2">{app.ai_symptoms_summary}</p>
                </div>
                <div className="text-right">
                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${app.status === 'Pending' ? 'bg-yellow-100 text-yellow-800' : app.status === 'Confirmed' ? 'bg-green-100 text-green-800' : app.status === 'Routing' ? 'bg-blue-100 text-blue-800' : 'bg-red-100 text-red-800'}`}>
                    {app.status}
                  </span>
                  <div className="mt-4 text-sm text-slate-500">
                    {app.date}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
