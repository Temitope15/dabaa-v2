'use client';

import { useState, useEffect } from 'react';
import { sendMessageToDaaba, Doctor } from '@/lib/api';
import { DoctorCard } from '@/components/DoctorCard';
import RideMap from '@/components/RideMap';
import ReactMarkdown from 'react-markdown';
import { motion, AnimatePresence } from 'framer-motion';
import { ArrowRight, Activity } from 'lucide-react';

interface SlideData {
  id: number;
  question: string;
  isFinal: boolean;
  doctors?: Doctor[];
  events?: string[];
}

export default function ChatPage() {
  const [userName, setUserName] = useState('');
  const [slides, setSlides] = useState<SlideData[]>([]);
  const [currentSlideIndex, setCurrentSlideIndex] = useState(0);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [activeEvents, setActiveEvents] = useState<string[]>([]);
  
  // States for Map view
  const [selectedDoctor, setSelectedDoctor] = useState<string | number | null>(null);
  const [bookingState, setBookingState] = useState<Record<string | number, 'idle' | 'loading' | 'success'>>({});
  
  const [errorToast, setErrorToast] = useState<string | null>(null);

  const [showApiKeyModal, setShowApiKeyModal] = useState(false);
  const [tempApiKey, setTempApiKey] = useState('');

  useEffect(() => {
    const name = localStorage.getItem('user_name');
    if (name) {
      setUserName(name.split(' ')[0]);
    }
    
    const existingKey = localStorage.getItem('gemini_api_key');
    if (!existingKey) {
      setShowApiKeyModal(true);
    }
    
    setSlides([
      {
        id: 0,
        question: `Welcome ${name ? name.split(' ')[0] : ''}, how are you feeling today?`,
        isFinal: false,
      }
    ]);
  }, []);

  const saveApiKey = () => {
    if (tempApiKey.trim()) {
      localStorage.setItem('gemini_api_key', tempApiKey.trim());
    }
    setShowApiKeyModal(false);
  };

  // Auto-hide toast after 5 seconds
  useEffect(() => {
    if (errorToast) {
      const timer = setTimeout(() => setErrorToast(null), 5000);
      return () => clearTimeout(timer);
    }
  }, [errorToast]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage = input.trim();
    setInput('');
    setIsLoading(true);
    setErrorToast(null);

    try {
      const response = await sendMessageToDaaba(userMessage);
      
      // If the backend returned an explicit error object disguised as a message
      if (response.text.startsWith("Error:") || response.text.includes("Quota Exceeded")) {
          setErrorToast(response.text);
          setIsLoading(false);
          // Restore input so user doesn't lose their message
          setInput(userMessage);
          return;
      }

      const isFinal = (response.doctors && response.doctors.length > 0) || response.text.length > 500;
      
      if (response.events) {
        setActiveEvents(response.events);
      }

      setSlides(prev => [...prev, {
        id: Date.now(),
        question: response.text,
        isFinal: isFinal,
        doctors: response.doctors,
      }]);
      setCurrentSlideIndex(prev => prev + 1);

    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || error.message || "Network error. Please try again.";
      setErrorToast(errorMsg);
      setInput(userMessage); // restore input
    } finally {
      setIsLoading(false);
    }
  };

  const handleBooking = (doctorId: string | number) => {
    setBookingState(prev => ({ ...prev, [doctorId]: 'loading' as const }));
    setTimeout(() => {
      setBookingState(prev => ({ ...prev, [doctorId]: 'success' as const }));
    }, 1500);
  };

  const currentSlide = slides[currentSlideIndex];

  if (!currentSlide) return null;

  return (
    <div className="flex h-full flex-col bg-slate-50 relative overflow-hidden">
      
      {/* API Key Modal */}
      <AnimatePresence>
        {showApiKeyModal && (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="absolute inset-0 z-[100] flex items-center justify-center bg-slate-900/40 backdrop-blur-sm p-4"
          >
            <motion.div 
              initial={{ scale: 0.95, y: 20 }}
              animate={{ scale: 1, y: 0 }}
              className="bg-white rounded-2xl shadow-xl w-full max-w-md overflow-hidden"
            >
              <div className="p-6 border-b border-slate-100">
                <h2 className="text-xl font-bold text-slate-900">Add API Key</h2>
                <p className="text-sm text-slate-500 mt-1">To ensure uninterrupted service, please provide your own free Gemini or OpenRouter (Claude) API key.</p>
              </div>
              
              <div className="p-6 space-y-4 bg-slate-50/50">
                <div>
                  <label className="block text-sm font-semibold text-slate-700 mb-1">Your API Key</label>
                  <input 
                    type="password"
                    value={tempApiKey}
                    onChange={(e) => setTempApiKey(e.target.value)}
                    placeholder="AIzaSy... or sk-or-..."
                    className="w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 outline-none transition-all font-mono text-sm"
                  />
                </div>
                
                <div className="bg-blue-50 text-blue-800 text-xs p-3 rounded-xl border border-blue-100">
                  <p className="font-semibold mb-1">Supported Providers:</p>
                  <ul className="list-disc pl-4 space-y-1">
                    <li><a href="https://aistudio.google.com/app/apikey" target="_blank" rel="noopener noreferrer" className="font-bold underline hover:text-blue-900">Google Gemini (AI Studio)</a></li>
                    <li><a href="https://openrouter.ai/keys" target="_blank" rel="noopener noreferrer" className="font-bold underline hover:text-blue-900">OpenRouter (Claude 3.5 Sonnet)</a></li>
                  </ul>
                </div>
              </div>
              
              <div className="p-4 bg-slate-50 border-t border-slate-100 flex justify-end gap-3">
                <button 
                  onClick={() => setShowApiKeyModal(false)}
                  className="px-5 py-2.5 text-sm font-semibold text-slate-600 hover:bg-slate-200 rounded-xl transition-colors"
                >
                  Skip for now
                </button>
                <button 
                  onClick={saveApiKey}
                  className="px-5 py-2.5 text-sm font-semibold bg-blue-600 hover:bg-blue-700 text-white rounded-xl shadow-sm transition-colors"
                >
                  Save Key
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Header - Make it floating when in map view */}
      <header className={`p-6 md:p-8 flex items-center justify-between z-50 ${currentSlide.isFinal ? 'absolute top-0 w-full pointer-events-none' : ''}`}>
        <div className="flex items-center gap-3 bg-white/85 backdrop-blur px-4 py-2 rounded-full shadow-sm border border-slate-100 pointer-events-auto">
          <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center text-xl shadow-sm">
            👩🏽‍⚕️
          </div>
          <div>
            <h1 className="font-bold text-slate-900 leading-tight">Nurse Daaba</h1>
            <p className="text-xs text-slate-500 font-medium">Triage Assistant</p>
          </div>
        </div>
        
        {/* Global Agent State Tracker */}
        {activeEvents.length > 0 && !currentSlide.isFinal && (
          <div className="flex flex-col items-end gap-1">
            <div className="flex items-center gap-2 text-xs font-semibold text-slate-600 bg-blue-50 px-3 py-1.5 rounded-full border border-blue-100">
              <Activity className="w-3 h-3 text-blue-500 animate-pulse" />
              {activeEvents[activeEvents.length - 1]}
            </div>
          </div>
        )}
      </header>

      {/* Error Toast */}
      <AnimatePresence>
        {errorToast && (
          <motion.div
            initial={{ opacity: 0, y: -20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -20, scale: 0.95 }}
            className="absolute top-24 left-1/2 -translate-x-1/2 z-[1000] w-full max-w-md pointer-events-auto"
          >
            <div className="mx-4 bg-white border border-red-200 rounded-xl shadow-lg p-4 flex gap-3 items-start relative">
              <div className="w-8 h-8 rounded-full bg-red-100 flex items-center justify-center shrink-0 text-red-600">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><path d="M12 9v4"/><path d="M12 17h.01"/></svg>
              </div>
              <div className="pt-0.5 flex-1">
                <h4 className="text-sm font-bold text-slate-900 mb-1">Request Failed</h4>
                <p className="text-xs text-slate-600 leading-snug break-words">
                  {errorToast}
                </p>
              </div>
              <button 
                onClick={() => setErrorToast(null)}
                className="text-slate-400 hover:text-slate-600 absolute top-3 right-3"
              >
                <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M18 6 6 18"/><path d="m6 6 12 12"/></svg>
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Main Area */}
      {currentSlide.isFinal ? (
        /* Ride-Hailing Map View */
        <div className="absolute inset-0 flex flex-col justify-end">
          {/* Full-bleed Map */}
          <RideMap 
            doctors={currentSlide.doctors || []} 
            selectedDoctorId={selectedDoctor}
            onDoctorSelect={setSelectedDoctor}
          />
          
          {/* Bottom Sheet Drawer */}
          <motion.div 
            initial={{ y: "100%" }}
            animate={{ y: 0 }}
            transition={{ type: "spring", damping: 25, stiffness: 200 }}
            className="z-40 w-full bg-white rounded-t-3xl shadow-[0_-10px_40px_rgba(0,0,0,0.1)] flex flex-col"
            style={{ maxHeight: "75vh" }}
          >
            {/* Drawer Handle */}
            <div className="w-full py-4 flex justify-center cursor-pointer shrink-0">
              <div className="w-12 h-1.5 bg-slate-200 rounded-full"></div>
            </div>

            <div className="px-6 pb-6 overflow-y-auto custom-scrollbar">
              <h2 className="text-2xl font-bold text-slate-900 mb-2">Triage Complete</h2>
              
              {/* Triage Summary Accordion-style */}
              <div className="bg-slate-50 p-4 rounded-2xl mb-6">
                <h3 className="text-sm font-bold text-slate-700 mb-2 uppercase tracking-wider">Health Report</h3>
                <div className="prose prose-sm prose-slate max-w-none prose-headings:text-slate-800">
                  <ReactMarkdown>{currentSlide.question}</ReactMarkdown>
                </div>
              </div>

              {/* Doctor / Hospital Selection */}
              <h3 className="text-lg font-bold text-slate-900 mb-4">Nearby Specialists</h3>
              
              <div className="flex gap-4 overflow-x-auto pb-4 custom-scrollbar snap-x snap-mandatory">
                {currentSlide.doctors?.map(doc => {
                  const isSelected = selectedDoctor === doc.id;
                  return (
                    <div 
                      key={doc.id}
                      onClick={() => setSelectedDoctor(doc.id)}
                      className={`snap-center shrink-0 w-72 md:w-80 cursor-pointer rounded-2xl border-2 transition-all p-4 ${
                        isSelected ? 'border-blue-600 bg-blue-50 shadow-md' : 'border-slate-100 bg-white hover:border-slate-200'
                      }`}
                    >
                      <div className="flex justify-between items-start mb-3">
                        <div>
                          <h4 className="font-bold text-slate-900">{doc.name}</h4>
                          <p className="text-sm text-blue-600 font-medium">{doc.specialty}</p>
                        </div>
                        <div className="bg-white px-2 py-1 rounded-lg text-xs font-bold text-slate-600 border border-slate-100 shadow-sm flex items-center gap-1">
                          <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 2v20"/><path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/></svg>
                          Free Consult
                        </div>
                      </div>
                      
                      <div className="flex items-center gap-2 text-sm text-slate-500 mb-4">
                        <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></svg>
                        {doc.distance_km}km away
                        {doc.is_hospital ? ' • Facility' : ' • Doctor'}
                      </div>

                      <button 
                        onClick={(e) => {
                          e.stopPropagation();
                          handleBooking(doc.id);
                        }}
                        className={`w-full py-2.5 rounded-xl font-medium transition-colors ${
                          isSelected ? 'bg-blue-600 text-white shadow-md hover:bg-blue-700' : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                        }`}
                      >
                        {bookingState[doc.id] === 'loading' ? (
                          <div className="w-5 h-5 border-2 border-current border-t-transparent rounded-full animate-spin mx-auto"></div>
                        ) : bookingState[doc.id] === 'success' ? (
                          doc.is_hospital ? 'Directions Sent!' : 'Request Sent!'
                        ) : (
                          doc.is_hospital ? 'Get Directions' : 'Book Appointment'
                        )}
                      </button>
                    </div>
                  );
                })}
              </div>
            </div>
          </motion.div>
        </div>
      ) : (
        /* Standard Chat Slide View */
        <main className="flex-1 relative flex items-center justify-center p-6 md:p-12 overflow-y-auto">
          <AnimatePresence mode="wait">
            <motion.div
              key={currentSlide.id}
              initial={{ opacity: 0, x: 50 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -50 }}
              transition={{ duration: 0.4, ease: "easeInOut" }}
              className="w-full max-w-3xl"
            >
              <div className="flex flex-col items-start gap-8">
                <div className="prose prose-slate prose-xl md:prose-2xl font-semibold text-slate-800 leading-tight max-w-none">
                  <ReactMarkdown>{currentSlide.question}</ReactMarkdown>
                </div>
                
                <form onSubmit={handleSubmit} className="w-full relative mt-8">
                  <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder="Type your answer here..."
                    disabled={isLoading}
                    autoFocus
                    className="w-full bg-transparent border-b-2 border-slate-300 focus:border-blue-600 text-2xl md:text-3xl py-4 pr-16 outline-none transition-all text-slate-900 placeholder:text-slate-300 disabled:opacity-50"
                  />
                  <button
                    type="submit"
                    disabled={!input.trim() || isLoading}
                    className="absolute right-0 top-1/2 -translate-y-1/2 p-3 bg-blue-600 text-white rounded-xl hover:bg-blue-700 disabled:opacity-30 disabled:hover:bg-blue-600 transition-all flex items-center justify-center shadow-sm"
                  >
                    {isLoading ? (
                      <div className="w-6 h-6 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                    ) : (
                      <ArrowRight className="w-6 h-6" />
                    )}
                  </button>
                </form>
                {isLoading && (
                  <p className="text-sm text-slate-500 animate-pulse mt-2 flex items-center gap-2">
                    <Activity className="w-4 h-4" /> Nurse Daaba is typing...
                  </p>
                )}
              </div>
            </motion.div>
          </AnimatePresence>
        </main>
      )}
    </div>
  );
}
