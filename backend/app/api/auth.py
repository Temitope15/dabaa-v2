from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from pydantic import BaseModel

from app.core.database import SessionLocal
from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.core.security import verify_password, get_password_hash, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES

router = APIRouter()

import datetime

class UserCreate(BaseModel):
    full_name: str
    email: str
    password: str
    phone_number: str
    date_of_birth: str = None
    role: str = "patient"

@router.post("/register")
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_in.email).first()
    if user:
        raise HTTPException(status_code=400, detail="Email already registered")
        
    new_user = User(
        full_name=user_in.full_name,
        email=user_in.email,
        phone_number=user_in.phone_number,
        hashed_password=get_password_hash(user_in.password),
        role=user_in.role
    )
    if user_in.date_of_birth:
        new_user.date_of_birth = datetime.date.fromisoformat(user_in.date_of_birth)
        
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Auto-login after registration
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=new_user.id, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer", "user_id": new_user.id, "full_name": new_user.full_name, "role": new_user.role}


@router.post("/login")
def login(db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=user.id, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer", "user_id": user.id, "full_name": user.full_name, "role": user.role}

@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    data = {
        "id": current_user.id,
        "full_name": current_user.full_name,
        "email": current_user.email,
        "phone_number": current_user.phone_number,
        "date_of_birth": current_user.date_of_birth,
        "role": current_user.role
    }
    if current_user.doctor_profile:
        data["doctor_profile"] = {
            "id": current_user.doctor_profile.id,
            "specialty": current_user.doctor_profile.specialty,
            "bio": current_user.doctor_profile.bio,
            "mdcn_number": current_user.doctor_profile.mdcn_number,
            "is_verified": current_user.doctor_profile.is_verified
        }
    return data
