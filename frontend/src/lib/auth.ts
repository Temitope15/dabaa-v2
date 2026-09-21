import axios from 'axios';

const API_URL = 'http://127.0.0.1:8000/api/auth';

export const login = async (email: string, password: string) => {
  // OAuth2 expects form-urlencoded data
  const formData = new URLSearchParams();
  formData.append('username', email);
  formData.append('password', password);
  
  const res = await axios.post(`${API_URL}/login`, formData, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
  });
  
  if (res.data.access_token) {
    localStorage.setItem('token', res.data.access_token);
    localStorage.setItem('user_name', res.data.full_name);
    if (res.data.role) localStorage.setItem('user_role', res.data.role);
  }
  return res.data;
};

export const register = async (data: { full_name: string, email: string, password: string, phone_number: string, date_of_birth: string, role: string }) => {
  const res = await axios.post(`${API_URL}/register`, data);
  if (res.data.access_token) {
    localStorage.setItem('token', res.data.access_token);
    localStorage.setItem('user_name', res.data.full_name);
    if (res.data.role) localStorage.setItem('user_role', res.data.role);
  }
  return res.data;
};

export const logout = () => {
  localStorage.removeItem('token');
  localStorage.removeItem('user_name');
  localStorage.removeItem('user_role');
};

import { api } from './api';
export const getProfile = async () => {
  const res = await api.get('/auth/me');
  return res.data;
};
