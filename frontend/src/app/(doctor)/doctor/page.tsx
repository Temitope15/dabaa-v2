'use client';

import { useEffect, useState } from 'react';
import { api } from '@/lib/api';
import Link from 'next/link';

export default function DoctorDashboardPage() {
  const [userName, setUserName] = useState('');
  const [stats, setStats] = useState({ total: 0, pending: 0, confirmed: 0 });
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const name = localStorage.getItem('user_name');
    if (name) setUserName(name);

    const fetchAppointments = async () => {
      try {
        const res = await api.get('/doctor/appointments');
        const appointments = res.data;
        const pending = appointments.filter((a: any) => a.status === 'Pending').length;
        const confirmed = appointments.filter((a: any) => a.status === 'Confirmed').length;
        setStats({ total: appointments.length, pending, confirmed });
      } catch (err) {
        console.error('Failed to fetch stats', err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchAppointments();
  }, []);

  return (
    <div className="flex-1 overflow-y-auto p-8">
      <div className="max-w-4xl mx-auto space-y-8">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Doctor Dashboard</h1>
          <p className="mt-2 text-slate-600">Welcome back, Dr. {userName}</p>
        </div>

        {isLoading ? (
          <div>Loading stats...</div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 flex flex-col items-center justify-center">
              <span className="text-sm font-medium text-slate-500 mb-1">Total Appointments</span>
              <span className="text-4xl font-bold text-slate-900">{stats.total}</span>
            </div>
            <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 flex flex-col items-center justify-center">
              <span className="text-sm font-medium text-slate-500 mb-1">Pending Requests</span>
              <span className="text-4xl font-bold text-yellow-600">{stats.pending}</span>
            </div>
            <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200 flex flex-col items-center justify-center">
              <span className="text-sm font-medium text-slate-500 mb-1">Confirmed</span>
              <span className="text-4xl font-bold text-green-600">{stats.confirmed}</span>
            </div>
          </div>
        )}

        <div>
          <Link href="/doctor/appointments" className="inline-flex items-center justify-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500">
            View Appointments
          </Link>
        </div>
      </div>
    </div>
  );
}
