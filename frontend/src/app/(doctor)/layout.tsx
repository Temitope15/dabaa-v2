'use client';

import { DoctorSidebar } from '@/components/DoctorSidebar';
import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function DoctorLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      router.push('/login');
      return;
    }
    const role = localStorage.getItem('user_role');
    if (role !== 'doctor') {
      router.push('/chat');
    }
  }, [router]);

  return (
    <div className="flex h-screen bg-slate-50 overflow-hidden">
      <DoctorSidebar />
      <div className="flex-1 overflow-hidden flex flex-col">
        {children}
      </div>
    </div>
  );
}
