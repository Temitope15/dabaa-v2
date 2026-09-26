# Dààbà | AI Medical Triage & Referral System

Dààbà (Yoruba for "Protection/Safety") is a smart, deterministic clinical triage and referral application designed for the Nigerian healthcare context. 

It acts as a digital first-responder, asking patients about their symptoms, analyzing them against a robust rule-based clinical expert system (containing nearly 500 diseases), and referring them to the most appropriate medical specialist or nearby hospital via an interactive map.

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

### Test Case A: The Patient Triage Flow
1. Open your browser and go to `http://localhost:3000`.
2. Click **"Get Started"** and sign up as a **Patient**. Fill in dummy details (Name, Email, Password, Phone, DOB).
3. Once registered, you will be redirected to the Chat interface with **Nurse Daaba**.
4. **Turn 1:** Type a symptom (e.g., *"I have a severe headache"*). 
5. **Turn 2:** The system will deterministically extract your symptom and ask for duration/severity. Reply with *"Since yesterday."*
6. **Turn 3:** The Expert System will scan its 500-disease database, find matching illnesses, and ask if you have related unmentioned symptoms (e.g., fever, nausea). Reply *"Yes, I have a fever."*
7. **The Result:** The system will calculate the highest probability disease (e.g., Malaria) and recommend a specific specialist (e.g., General Practitioner).
8. **The Map:** An interactive OpenStreetMap will immediately appear, dropping a pin on your location and showing nearby appropriate hospitals/doctors.
9. Click **"Book Appointment"** on one of the hospital cards. A "Booking Confirmed!" success message will appear.

### Test Case B: The Doctor Dashboard
1. Go back to `http://localhost:3000/signup`.
2. This time, select the **"I'm a Doctor"** toggle at the top of the form.
3. Notice how the form dynamically expands to ask for your **Specialty**, **MDCN License Number**, and **Bio**.
4. Fill in the details (ensure your MDCN number format matches standard practice, e.g., `MDCN-123456` if validation is active) and register.
5. You will be redirected to the **Doctor Portal** (`/doctor`), where you can view your analytics, pending appointment requests from patients, and update your clinical profile.

---


