from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
from typing import List
import logging

import models
import schemas
import auth
from database import engine, get_db
from config import settings
from scheduler import start_scheduler, shutdown_scheduler

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Dead Man's Switch API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    start_scheduler()
    logger.info("Application started")


@app.on_event("shutdown")
async def shutdown_event():
    shutdown_scheduler()
    logger.info("Application shutdown")


@app.get("/")
async def root():
    return {"message": "Dead Man's Switch API", "version": "1.0.0"}


@app.post("/api/auth/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check if user exists
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    hashed_password = auth.get_password_hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user


@app.post("/api/auth/login", response_model=schemas.Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/api/auth/me", response_model=schemas.UserResponse)
async def get_current_user_info(current_user: models.User = Depends(auth.get_current_user)):
    return current_user


@app.post("/api/switches", response_model=schemas.SwitchResponse, status_code=status.HTTP_201_CREATED)
async def create_switch(
    switch: schemas.SwitchCreate,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    # Create switch
    db_switch = models.Switch(
        user_id=current_user.id,
        name=switch.name,
        check_in_interval_days=switch.check_in_interval_days,
        last_check_in=datetime.utcnow()
    )
    db.add(db_switch)
    db.flush()
    
    # Create messages
    for msg in switch.messages:
        db_message = models.Message(
            switch_id=db_switch.id,
            recipient_email=msg.recipient_email,
            subject=msg.subject,
            body=msg.body
        )
        db.add(db_message)
    
    db.commit()
    db.refresh(db_switch)
    
    return db_switch


@app.get("/api/switches", response_model=List[schemas.SwitchResponse])
async def get_switches(
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    switches = db.query(models.Switch).filter(models.Switch.user_id == current_user.id).all()
    return switches


@app.get("/api/switches/{switch_id}", response_model=schemas.SwitchResponse)
async def get_switch(
    switch_id: int,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    switch = db.query(models.Switch).filter(
        models.Switch.id == switch_id,
        models.Switch.user_id == current_user.id
    ).first()
    
    if not switch:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Switch not found")
    
    return switch


@app.patch("/api/switches/{switch_id}", response_model=schemas.SwitchResponse)
async def update_switch(
    switch_id: int,
    switch_update: schemas.SwitchUpdate,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    switch = db.query(models.Switch).filter(
        models.Switch.id == switch_id,
        models.Switch.user_id == current_user.id
    ).first()
    
    if not switch:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Switch not found")
    
    if switch_update.name is not None:
        switch.name = switch_update.name
    if switch_update.check_in_interval_days is not None:
        switch.check_in_interval_days = switch_update.check_in_interval_days
    if switch_update.is_active is not None:
        switch.is_active = switch_update.is_active
    
    db.commit()
    db.refresh(switch)
    
    return switch


@app.post("/api/switches/{switch_id}/checkin", response_model=schemas.SwitchResponse)
async def check_in(
    switch_id: int,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    switch = db.query(models.Switch).filter(
        models.Switch.id == switch_id,
        models.Switch.user_id == current_user.id
    ).first()
    
    if not switch:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Switch not found")
    
    if switch.is_triggered:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot check in to a triggered switch"
        )
    
    switch.last_check_in = datetime.utcnow()
    db.commit()
    db.refresh(switch)
    
    return switch


@app.delete("/api/switches/{switch_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_switch(
    switch_id: int,
    current_user: models.User = Depends(auth.get_current_user),
    db: Session = Depends(get_db)
):
    switch = db.query(models.Switch).filter(
        models.Switch.id == switch_id,
        models.Switch.user_id == current_user.id
    ).first()
    
    if not switch:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Switch not found")
    
    db.delete(switch)
    db.commit()
    
    return None
