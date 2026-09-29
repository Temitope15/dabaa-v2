# Dààbà | AI Medical Triage & Referral System

Dààbà (Yoruba for "Protection/Safety") is a smart, deterministic clinical triage and referral application designed for the Nigerian healthcare context. 

It acts as a digital first-responder, asking patients about their symptoms, analyzing them against a robust rule-based clinical agent (containing nearly 500 diseases), and referring them to the most appropriate medical specialist or nearby hospital via an interactive map.

---

## 🚀 Quick Start Guide

This project is a monorepo consisting of a **FastAPI backend** and a **Next.js frontend**. You will need to run both concurrently in separate terminal windows.

### 1. Backend Setup (FastAPI / Python)

Open your first terminal and navigate to the backend folder:
```bash
cd backend
```

**Step 1: Create a virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

**Step 2: Install dependencies**
```bash
pip install -r requirements.txt
```

**Step 3: Setup Environment Variables**
Create a `.env` file in the `backend` folder and paste the following secrets exactly as they are:
```env
DATABASE_URL=postgresql://neondb_owner:npg_YOuWh3vlzoe0@ep-steep-bread-b45vli87-pooler.c-6.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require
SECRET_KEY=d1c957b56e1216ef3ef64087edcbac43cbd82791c1d62eeb86de1e395a087c70
```

**Step 4: Run the server**
```bash
uvicorn app.main:app --reload
```
*The backend will now be running on `http://127.0.0.1:8000`.*

---

### 2. Frontend Setup (Next.js / React)

Open a **second** terminal and navigate to the frontend folder:
```bash
cd frontend
```

**Step 1: Install dependencies**
```bash
npm install
# or
yarn install
```

**Step 2: Setup Environment Variables**
Create a `.env.local` file in the `frontend` folder and add:
```env
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

**Step 3: Run the development server**
```bash
npm run dev
# or
yarn dev
```
*The frontend will now be running on `http://localhost:3000`.*

---

## 🧪 Step-by-Step Testing Guidelines

To fully experience the application exactly as intended, please follow this specific testing flow:

### Test Case: The Patient Triage Flow
1. Open your browser and go to `http://localhost:3000`.
2. Review the modern landing page and click **"Meet Nurse Daaba 😊"** or **"Sign up"**. 
3. Sign up for a Daaba account by filling in dummy details (Name, Email, Password, Phone, DOB).
4. Once registered, you will be seamlessly redirected to the Chat interface with **Nurse Daaba**.
5. **Turn 1:** Type a symptom colloquially (e.g., *"I have a severe headache"* or *"I am feeling cold"*). 
6. **Dynamic Triage:** The system deterministically extracts your symptoms (using a custom synonym mapper for slang) and asks for follow-up symptoms dynamically. 
7. **The Loop:** It continues narrowing down using a rule-based inference engine against nearly 500 diseases until it hits an 80% algorithmic confidence threshold.
8. **The Diagnosis:** Once confident (or after 10 turns), it will calculate the highest probability disease, present a triage summary, and recommend a specific specialist (e.g., General Practitioner).
9. **Smart Geo-Routing:** An interactive map will immediately appear. The system queries the OpenStreetMap (OSM) Overpass API to find actual hospitals or specific specialists near your location.
10. **Directions:** Click **"Get Directions"** on one of the hospital cards. Your browser will prompt for geolocation, and automatically open a new tab to Google Maps with turn-by-turn directions from your exact spot to the hospital!
11. **Appointments/Dashboard:** Navigate to your Appointments page from the sidebar to view your complete saved AI Triage Summary and retrieve the routing directions at any time.

---


