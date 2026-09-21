import axios from 'axios';

const BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';
const API_URL = `${BASE_URL}/api`;

// Create an axios instance
export const api = axios.create({
  baseURL: API_URL,
});

// Add interceptor to inject token
api.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('token');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
  }
  return config;
});

export interface Doctor {
  id: number | string;
  name: string;
  specialty: string;
  bio: string;
  lat?: number;
  lng?: number;
  distance_km: number;
  is_hospital?: boolean;
}

export interface ChatResponse {
  text: string;
  doctors: Doctor[];
  events: string[];
}

// Legacy non-streaming endpoint (kept as fallback)
export const sendMessageToDaaba = async (message: string): Promise<ChatResponse> => {
  const apiKey = typeof window !== 'undefined' ? localStorage.getItem('gemini_api_key') : null;
  const response = await api.post('/chat', {
    message,
    lat: 6.5244,
    lng: 3.3792,
    api_key: apiKey
  });
  return response.data;
};

// Streaming endpoint using SSE
export interface StreamCallbacks {
  onToken: (token: string) => void;
  onEvents: (events: string[]) => void;
  onDoctors: (doctors: Doctor[]) => void;
  onDone: () => void;
  onError: (error: string) => void;
}

export const streamMessageToDaaba = async (message: string, callbacks: StreamCallbacks): Promise<void> => {
  const token = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
  const apiKey = typeof window !== 'undefined' ? localStorage.getItem('gemini_api_key') : null;

  const response = await fetch(`${API_URL}/chat/stream`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
    },
    body: JSON.stringify({
      message,
      lat: 6.5244,
      lng: 3.3792,
      api_key: apiKey,
    }),
  });

  if (!response.ok) {
    callbacks.onError(`Server error: ${response.status}`);
    callbacks.onDone();
    return;
  }

  const reader = response.body?.getReader();
  if (!reader) {
    callbacks.onError('No response body');
    callbacks.onDone();
    return;
  }

  const decoder = new TextDecoder();
  let buffer = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split('\n');
    buffer = lines.pop() || ''; // Keep incomplete line in buffer

    for (const line of lines) {
      if (line.startsWith('data: ')) {
        try {
          const payload = JSON.parse(line.slice(6));
          switch (payload.type) {
            case 'token':
              callbacks.onToken(payload.data);
              break;
            case 'text':
              // Full text (used for error messages)
              callbacks.onToken(payload.data);
              break;
            case 'event':
              callbacks.onEvents([payload.data]);
              break;
            case 'events':
              callbacks.onEvents(payload.data);
              break;
            case 'doctors':
              callbacks.onDoctors(payload.data);
              break;
            case 'done':
              callbacks.onDone();
              return;
          }
        } catch {
          // Skip malformed JSON lines
        }
      }
    }
  }

  callbacks.onDone();
};

export const bookAppointment = async (doctorId: number | string): Promise<{ message: string }> => {
  const response = await api.post('/book', {
    doctor_id: doctorId,
  });
  return response.data;
};
