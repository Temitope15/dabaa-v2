'use client';

import { useEffect, useState } from 'react';
import { getProfile } from '@/lib/auth';

export default function ProfilePage() {
  const [profile, setProfile] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [apiKey, setApiKey] = useState('');

  useEffect(() => {
    const savedKey = localStorage.getItem('gemini_api_key');
    if (savedKey) setApiKey(savedKey);
    
    getProfile()
      .then(data => setProfile(data))
      .catch(err => console.error("Failed to load profile", err))
      .finally(() => setIsLoading(false));
  }, []);

  if (isLoading) {
    return <div className="flex justify-center items-center h-full"><p>Loading profile...</p></div>;
  }

  if (!profile) {
    return <div className="flex justify-center items-center h-full"><p>Error loading profile.</p></div>;
  }

  // Get initials
  const initials = profile.full_name ? profile.full_name.split(' ').map((n: string) => n[0]).join('').substring(0, 2).toUpperCase() : 'U';

  const handleApiKeyChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const key = e.target.value;
    setApiKey(key);
    if (key) {
      localStorage.setItem('gemini_api_key', key);
    } else {
      localStorage.removeItem('gemini_api_key');
    }
  };

  return (
    <div className="flex flex-col h-full bg-slate-50 relative p-8">
      <div className="max-w-3xl mx-auto w-full mt-8">
        <h1 className="text-3xl font-bold text-slate-900 mb-6">Profile Settings</h1>
        
        <div className="bg-white rounded-2xl border border-slate-200 p-8 shadow-sm">
          <div className="flex items-center gap-4 mb-8 pb-8 border-b border-slate-100">
            <div className="w-20 h-20 bg-slate-200 rounded-full flex items-center justify-center text-slate-500 text-3xl font-bold">
              {initials}
            </div>
            <div>
              <h2 className="text-2xl font-bold text-slate-900">{profile.full_name}</h2>
              <p className="text-slate-500">{profile.email}</p>
            </div>
          </div>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Custom Gemini API Key</label>
              <input 
                type="password" 
                value={apiKey} 
                onChange={handleApiKeyChange}
                placeholder="Paste your Gemini API Key here" 
                className="w-full bg-white border border-slate-300 rounded-lg px-4 py-2 text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500" 
              />
              <p className="text-xs text-slate-500 mt-1">Stored locally in your browser. Used to bypass global server quotas.</p>
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Phone Number</label>
              <input type="text" readOnly value={profile.phone_number || ''} className="w-full bg-slate-100 border border-slate-200 rounded-lg px-4 py-2 text-slate-900 focus:outline-none" />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Date of Birth</label>
              <input type="text" readOnly value={profile.date_of_birth || 'Not provided'} className="w-full bg-slate-100 border border-slate-200 rounded-lg px-4 py-2 text-slate-900 focus:outline-none" />
            </div>
            <p className="text-xs text-slate-400 mt-4">Profile editing is disabled in the MVP prototype.</p>
          </div>
        </div>
      </div>
    </div>
  );
}
