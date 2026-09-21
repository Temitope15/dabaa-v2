export default function AppointmentsPage() {
  return (
    <div className="flex flex-col h-full bg-slate-50 relative p-8">
      <div className="max-w-3xl mx-auto w-full mt-8">
        <h1 className="text-3xl font-bold text-slate-900 mb-6">Appointments</h1>
        
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
      </div>
    </div>
  );
}
