'use client';

import { useState, useEffect } from 'react';
import { api } from '@/lib/api';

export default function DoctorProfilePage() {
  const [formData, setFormData] = useState({
    specialty: 'General Practitioner',
    bio: '',
    mdcn_number: '',
    lat: 0,
    lng: 0
  });
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const res = await api.get('/auth/me'); // Or the specific doctor profile endpoint if that exists
        // Assuming the response includes doctor specific fields, we populate them.
        // If they are nested or in another endpoint, this needs adjustment based on actual backend design.
        if (res.data) {
           setFormData({
             specialty: res.data.specialty || 'General Practitioner',
             bio: res.data.bio || '',
             mdcn_number: res.data.mdcn_number || '',
             lat: res.data.lat || 0,
             lng: res.data.lng || 0
           });
        }
      } catch (err) {
        console.error('Failed to fetch profile', err);
      } finally {
        setIsLoading(false);
      }
    };
    fetchProfile();
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition((position) => {
        setFormData({
          ...formData,
          lat: position.coords.latitude,
          lng: position.coords.longitude
        });
      }, (err) => {
        alert('Could not get location: ' + err.message);
      });
    } else {
      alert('Geolocation is not supported by this browser.');
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);
    setMessage('');
    try {
      await api.post('/doctor/profile', formData);
      setMessage('Profile saved successfully!');
    } catch (err) {
      console.error(err);
      setMessage('Failed to save profile.');
    } finally {
      setIsSaving(false);
    }
  };

  if (isLoading) {
    return <div className="p-8">Loading profile...</div>;
  }

  return (
    <div className="flex-1 overflow-y-auto p-8">
      <div className="max-w-2xl mx-auto space-y-6">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">Doctor Profile</h1>
          <p className="mt-2 text-slate-600">Update your professional details and location.</p>
        </div>

        <div className="bg-white p-6 rounded-2xl shadow-sm border border-slate-200">
          <form onSubmit={handleSubmit} className="space-y-6">
            
            {message && (
              <div className={`p-3 rounded-md text-sm font-medium ${message.includes('success') ? 'bg-green-50 text-green-800' : 'bg-red-50 text-red-800'}`}>
                {message}
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-slate-700">Specialty</label>
              <div className="mt-1">
                <select
                  name="specialty"
                  required
                  value={formData.specialty}
                  onChange={handleChange}
                  className="appearance-none block w-full px-3 py-2 border border-slate-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm text-slate-900 bg-white"
                >
                  <option value="General Practitioner">General Practitioner</option>
                  <option value="Cardiologist">Cardiologist</option>
                  <option value="Dermatologist">Dermatologist</option>
                  <option value="Neurologist">Neurologist</option>
                  <option value="Orthopedic Surgeon">Orthopedic Surgeon</option>
                  <option value="Pediatrician">Pediatrician</option>
                  <option value="Psychiatrist">Psychiatrist</option>
                  <option value="ENT Specialist">ENT Specialist</option>
                  <option value="Gynecologist">Gynecologist</option>
                  <option value="Ophthalmologist">Ophthalmologist</option>
                </select>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700">MDCN License Number</label>
              <div className="mt-1">
                <input
                  name="mdcn_number"
                  type="text"
                  required
                  value={formData.mdcn_number}
                  onChange={handleChange}
                  className="appearance-none block w-full px-3 py-2 border border-slate-300 rounded-md shadow-sm placeholder-slate-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm text-slate-900"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700">Short Bio</label>
              <div className="mt-1">
                <textarea
                  name="bio"
                  required
                  rows={4}
                  value={formData.bio}
                  onChange={handleChange}
                  className="appearance-none block w-full px-3 py-2 border border-slate-300 rounded-md shadow-sm placeholder-slate-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm text-slate-900"
                ></textarea>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Location</label>
              <div className="flex gap-4 mb-2">
                <div className="flex-1">
                  <input
                    name="lat"
                    type="number"
                    step="any"
                    placeholder="Latitude"
                    value={formData.lat}
                    onChange={handleChange}
                    className="appearance-none block w-full px-3 py-2 border border-slate-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm text-slate-900"
                  />
                </div>
                <div className="flex-1">
                  <input
                    name="lng"
                    type="number"
                    step="any"
                    placeholder="Longitude"
                    value={formData.lng}
                    onChange={handleChange}
                    className="appearance-none block w-full px-3 py-2 border border-slate-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm text-slate-900"
                  />
                </div>
              </div>
              <button
                type="button"
                onClick={handleLocation}
                className="text-sm text-blue-600 font-medium hover:text-blue-500"
              >
                + Use My Current Location
              </button>
            </div>

            <div className="pt-4 border-t border-slate-100">
              <button
                type="submit"
                disabled={isSaving}
                className="w-full sm:w-auto flex justify-center py-2 px-6 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:bg-blue-400"
              >
                {isSaving ? 'Saving...' : 'Save Profile'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
