from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timezone
from app.db import get_db
from app.auth.dependencies import get_current_user
from app.models.availability import AvailabilityConfig, AvailabilityResponse

router = APIRouter(prefix="/availability", tags=["Availability"])

@router.get("", response_model=AvailabilityResponse)
async def get_availability(current_user: dict = Depends(get_current_user)):
    db = get_db()
    user_id = current_user["id"]
    avail = await db.availability.find_one({"user_id": user_id})
    if not avail:
        # Create default availability
        avail = {
            "user_id": user_id,
            "monday": 2.0,
            "tuesday": 2.0,
            "wednesday": 2.0,
            "thursday": 2.0,
            "friday": 2.0,
            "saturday": 4.0,
            "sunday": 4.0,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        res = await db.availability.insert_one(avail)
        avail["_id"] = res.inserted_id

    avail["id"] = str(avail["_id"])
    return AvailabilityResponse(**avail)

@router.put("", response_model=AvailabilityResponse)
async def update_availability(
    config: AvailabilityConfig,
    current_user: dict = Depends(get_current_user)
):
    db = get_db()
    user_id = current_user["id"]
    now = datetime.now(timezone.utc)
    
    update_doc = config.model_dump()
    update_doc["updated_at"] = now
    
    res = await db.availability.find_one_and_update(
        {"user_id": user_id},
        {"$set": update_doc},
        upsert=True,
        return_document=True
    )

    res["id"] = str(res["_id"])
    return AvailabilityResponse(**res)
