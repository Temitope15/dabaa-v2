import Link from 'next/link';

export default function Home() {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-slate-50 p-6">
      <main className="max-w-2xl text-center">
        <h1 className="text-4xl font-extrabold text-slate-900 mb-6">
          Welcome to Daaba
        </h1>
        <p className="text-lg text-slate-600 mb-12">
          Your AI-powered medical triage and referral assistant. Let's get you to the right care, faster.
        </p>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Link 
            href="/login"
            className="flex flex-col items-center p-8 bg-white border border-slate-200 rounded-2xl shadow-sm hover:shadow-md transition-shadow"
          >
            <div className="w-16 h-16 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center mb-4 text-2xl font-bold">
              +
            </div>
            <h2 className="text-xl font-semibold text-slate-800 mb-2">I am a Patient</h2>
            <p className="text-slate-500 text-sm">Talk to Daaba to check your symptoms and find nearby doctors.</p>
          </Link>

          <div className="flex flex-col items-center p-8 bg-white border border-slate-200 rounded-2xl shadow-sm opacity-50 cursor-not-allowed">
            <div className="w-16 h-16 bg-green-100 text-green-600 rounded-full flex items-center justify-center mb-4 text-2xl font-bold">
              👩‍⚕️
            </div>
            <h2 className="text-xl font-semibold text-slate-800 mb-2">I am a Doctor</h2>
            <p className="text-slate-500 text-sm">Sign up and manage your availability. (Coming soon)</p>
          </div>
        </div>
      </main>
    </div>
  );
}
