'use client';

import dynamic from 'next/dynamic';

const HospitalMap = dynamic(() => import('./HospitalMapClient'), {
  ssr: false,
  loading: () => (
    <div className="h-[400px] w-full bg-slate-100 animate-pulse rounded-xl flex items-center justify-center text-slate-400">
      Loading Map...
    </div>
  )
});

export default HospitalMap;
