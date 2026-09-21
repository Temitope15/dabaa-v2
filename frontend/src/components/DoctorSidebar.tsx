'use client';

import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { LayoutDashboard, Calendar, User, LogOut } from 'lucide-react';
import { logout } from '@/lib/auth';
import { useEffect, useState } from 'react';

export function DoctorSidebar() {
  const pathname = usePathname();
  const router = useRouter();
  const [userName, setUserName] = useState('Doctor');

  useEffect(() => {
    const name = localStorage.getItem('user_name');
    if (name) setUserName(name);
  }, []);

  const handleLogout = (e: React.MouseEvent) => {
    e.preventDefault();
    logout();
    router.push('/login');
  };

  const navItems = [
    { name: 'Dashboard', href: '/doctor', icon: LayoutDashboard },
    { name: 'Appointments', href: '/doctor/appointments', icon: Calendar },
    { name: 'Profile', href: '/doctor/profile', icon: User },
  ];

  return (
    <div className="w-64 bg-slate-900 text-slate-300 h-screen hidden md:flex flex-col flex-shrink-0">
      <div className="p-6">
        <h2 className="text-2xl font-bold text-white tracking-tight">Daaba</h2>
        <p className="text-sm text-slate-400 mt-1">Dr. {userName}</p>
      </div>

      <nav className="flex-1 px-4 space-y-2 mt-4">
        {navItems.map((item) => {
          const isActive = pathname === item.href;
          const Icon = item.icon;
          return (
            <Link
              key={item.name}
              href={item.href}
              className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-colors ${
                isActive 
                  ? 'bg-blue-600 text-white font-medium' 
                  : 'hover:bg-slate-800 hover:text-white'
              }`}
            >
              <Icon size={20} className={isActive ? 'text-white' : 'text-slate-400'} />
              {item.name}
            </Link>
          );
        })}
      </nav>

      <div className="p-4 border-t border-slate-800 mt-auto">
        <button 
          onClick={handleLogout}
          className="flex items-center gap-3 px-4 py-3 text-slate-400 hover:text-red-400 hover:bg-slate-800 rounded-xl transition-colors w-full text-left"
        >
          <LogOut size={20} />
          Sign Out
        </button>
      </div>
    </div>
  );
}
