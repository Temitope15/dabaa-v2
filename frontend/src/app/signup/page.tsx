'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { register } from '@/lib/auth';
import axios from 'axios';

export default function SignupPage() {
  const [role, setRole] = useState<'patient' | 'doctor'>('patient');
  const [formData, setFormData] = useState({
    full_name: '',
    email: '',
    phone_number: '',
    password: '',
    date_of_birth: '',
    specialty: 'General Practitioner',
    mdcn_number: '',
    bio: ''
  });
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const router = useRouter();

  const handleSignup = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      const res = await register({
        full_name: formData.full_name,
        email: formData.email,
        password: formData.password,
        phone_number: formData.phone_number,
        date_of_birth: formData.date_of_birth,
        role: role
      });

      if (role === 'doctor') {
        const BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';
        await axios.post(`${BASE_URL}/api/doctor/profile`, {
          specialty: formData.specialty,
          bio: formData.bio,
          mdcn_number: formData.mdcn_number,
          lat: 6.5244,
          lng: 3.3792
        }, {
          headers: { Authorization: `Bearer ${res.access_token}` }
        });
        router.push('/doctor');
      } else {
        router.push('/chat');
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Registration failed');
    } finally {
      setIsLoading(false);
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  return (
    <div className="min-h-screen bg-slate-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <h2 className="mt-6 text-center text-3xl font-extrabold text-slate-900">
          Create a Daaba account
        </h2>
        <p className="mt-2 text-center text-sm text-slate-600">
          Already have an account?{' '}
          <Link href="/login" className="font-medium text-blue-600 hover:text-blue-500">
            Sign in instead
          </Link>
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10 border border-slate-200">
          <div className="flex mb-6 bg-slate-100 p-1 rounded-lg">
            <button
              className={`flex-1 py-2 text-sm font-medium rounded-md ${role === 'patient' ? 'bg-white shadow text-slate-900' : 'text-slate-500 hover:text-slate-700'}`}
              onClick={() => setRole('patient')}
            >
              I'm a Patient
            </button>
            <button
              className={`flex-1 py-2 text-sm font-medium rounded-md ${role === 'doctor' ? 'bg-white shadow text-slate-900' : 'text-slate-500 hover:text-slate-700'}`}
              onClick={() => setRole('doctor')}
            >
              I'm a Doctor
            </button>
          </div>
          
          <form className="space-y-4" onSubmit={handleSignup}>
            {error && (
              <div className="bg-red-50 text-red-600 p-3 rounded-md text-sm font-medium">
                {error}
              </div>
            )}
            
            <div>
              <label className="block text-sm font-medium text-slate-700">Full Name</label>
              <div className="mt-1">
                <input
                  name="full_name"
                  type="text"
                  required
                  value={formData.full_name}
                  onChange={handleChange}
                  className="appearance-none block w-full px-3 py-2 border border-slate-300 rounded-md shadow-sm placeholder-slate-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm text-slate-900"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700">Email address</label>
              <div className="mt-1">
                <input
                  name="email"
                  type="email"
                  required
                  value={formData.email}
                  onChange={handleChange}
                  className="appearance-none block w-full px-3 py-2 border border-slate-300 rounded-md shadow-sm placeholder-slate-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm text-slate-900"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700">Phone Number</label>
              <div className="mt-1">
                <input
                  name="phone_number"
                  type="tel"
                  required
                  value={formData.phone_number}
                  onChange={handleChange}
                  placeholder="+234..."
                  className="appearance-none block w-full px-3 py-2 border border-slate-300 rounded-md shadow-sm placeholder-slate-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm text-slate-900"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700">Date of Birth</label>
              <div className="mt-1">
                <input
                  name="date_of_birth"
                  type="date"
                  required
                  value={formData.date_of_birth}
                  onChange={handleChange}
                  className="appearance-none block w-full px-3 py-2 border border-slate-300 rounded-md shadow-sm placeholder-slate-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm text-slate-900"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700">Password</label>
              <div className="mt-1">
                <input
                  name="password"
                  type="password"
                  required
                  value={formData.password}
                  onChange={handleChange}
                  className="appearance-none block w-full px-3 py-2 border border-slate-300 rounded-md shadow-sm placeholder-slate-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm text-slate-900"
                />
              </div>
            </div>

            {role === 'doctor' && (
              <>
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
                      rows={3}
                      value={formData.bio}
                      onChange={handleChange}
                      className="appearance-none block w-full px-3 py-2 border border-slate-300 rounded-md shadow-sm placeholder-slate-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm text-slate-900"
                    ></textarea>
                  </div>
                </div>
              </>
            )}

            <div className="pt-2">
              <button
                type="submit"
                disabled={isLoading}
                className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:bg-blue-400"
              >
                {isLoading ? 'Creating account...' : 'Create account'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
