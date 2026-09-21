import dynamic from 'next/dynamic';

const RideMapClient = dynamic(() => import('./RideMapClient'), {
  ssr: false,
  loading: () => (
    <div className="absolute inset-0 w-full h-full bg-slate-100 animate-pulse flex items-center justify-center z-0">
      <div className="text-slate-400 font-medium flex items-center gap-2">
        <div className="w-4 h-4 border-2 border-slate-400 border-t-transparent rounded-full animate-spin"></div>
        Loading Map...
      </div>
    </div>
  ),
});

export default RideMapClient;
