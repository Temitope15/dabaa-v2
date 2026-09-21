from fastapi import FastAPI
from dotenv import load_dotenv
import os

from fastapi.middleware.cors import CORSMiddleware

# Load env variables before importing routers
load_dotenv()

from app.api import chat, booking, auth, doctor

app = FastAPI(title="Daaba API", description="AI Healthcare Triage and Referral API")

# Configure CORS to allow Vercel deployments and local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ],
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(chat.router, prefix="/api", tags=["Chat"])
app.include_router(booking.router, prefix="/api", tags=["Booking"])
app.include_router(doctor.router, prefix="/api/doctor", tags=["Doctor"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the Daaba API"}
