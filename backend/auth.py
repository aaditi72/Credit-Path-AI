from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from database import SessionLocal
from models import User
import bcrypt
from typing import Optional
from datetime import datetime

router = APIRouter(prefix="/api/auth", tags=["Auth"])

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    created_at: datetime # Ensure datetime is imported from datetime
    class Config:
        orm_mode = True # Enables Pydantic to read data from ORM objects

class SignupRequest(BaseModel):
    name: str
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginSuccessResponse(BaseModel):
    message: str
    user: EmailStr # Return the email for display on frontend

@router.post("/signup", response_model=dict, status_code=status.HTTP_201_CREATED, summary="Register a new user account")
def signup(user: SignupRequest, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User with this email already exists")

    hashed = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt())
    new_user = User(name=user.name, email=user.email, password=hashed.decode('utf-8'))
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "Signup successful", "user_id": new_user.id}

@router.post("/login", response_model=LoginSuccessResponse, summary="Log in an existing user")
def login(user: LoginRequest, db: Session = Depends(get_db)):
    record = db.query(User).filter(User.email == user.email).first()
    if not record:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    if not bcrypt.checkpw(user.password.encode('utf-8'), record.password.encode('utf-8')):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password")

    return {"message": "Login successful", "user": record.email}