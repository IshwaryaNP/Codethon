from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime, timezone
from app.db import get_db
from app.models.user import UserRegister, UserLogin, UserResponse, TokenResponse
from app.auth.password import hash_password, verify_password
from app.auth.jwt import create_access_token
from app.auth.dependencies import get_current_user
from bson import ObjectId

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register", response_model=TokenResponse)
async def register(user_data: UserRegister):
    db = get_db()
    existing_user = await db.users.find_one({"email": user_data.email.lower()})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered"
        )
    
    hashed_pwd = hash_password(user_data.password)
    now = datetime.now(timezone.utc)
    new_user = {
        "name": user_data.name,
        "email": user_data.email.lower(),
        "password": hashed_pwd,
        "created_at": now,
        "updated_at": now
    }
    
    result = await db.users.insert_one(new_user)
    user_id = str(result.inserted_id)

    # Initialize default availability for new user
    default_avail = {
        "user_id": user_id,
        "monday": 2.0,
        "tuesday": 2.0,
        "wednesday": 2.0,
        "thursday": 2.0,
        "friday": 2.0,
        "saturday": 4.0,
        "sunday": 4.0,
        "created_at": now,
        "updated_at": now
    }
    await db.availability.update_one({"user_id": user_id}, {"$set": default_avail}, upsert=True)

    access_token = create_access_token(data={"sub": user_id, "email": user_data.email.lower()})
    
    user_resp = UserResponse(
        id=user_id,
        name=user_data.name,
        email=user_data.email.lower(),
        created_at=now
    )
    
    return TokenResponse(access_token=access_token, token_type="bearer", user=user_resp)

@router.post("/login", response_model=TokenResponse)
async def login(credentials: UserLogin):
    db = get_db()
    user = await db.users.find_one({"email": credentials.email.lower()})
    if not user or not verify_password(credentials.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    user_id = str(user["_id"])
    access_token = create_access_token(data={"sub": user_id, "email": user["email"]})
    
    user_resp = UserResponse(
        id=user_id,
        name=user["name"],
        email=user["email"],
        created_at=user.get("created_at", datetime.now(timezone.utc))
    )
    
    return TokenResponse(access_token=access_token, token_type="bearer", user=user_resp)

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    return UserResponse(
        id=current_user["id"],
        name=current_user["name"],
        email=current_user["email"],
        created_at=current_user.get("created_at", datetime.now(timezone.utc))
    )
