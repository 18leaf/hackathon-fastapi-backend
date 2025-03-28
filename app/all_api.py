from datetime import datetime
from typing import Annotated, Optional, List
from fastapi import APIRouter, HTTPException, status, Depends, Query
from fastapi.encoders import jsonable_encoder
from user_model import UserForm, UserAuth
from all_model import (
    UserProfileCreate, UserProfileDB,
    EventCreate, EventDB,
    AttendanceCreate, AttendanceDB,
)
from ai_model import AISummaryDB
from ai_integration import generate_recommendation
import all_crud
from authentication import get_password_hash, get_current_active_user

router = APIRouter()

# ---------------------------
# User Endpoints (Composite)
# ---------------------------


@router.post("/user/create_user")
async def create_user_endpoint(user: UserForm):
    # Validate uniqueness
    '''if user.email:
        email_user = await all_crud.get_user_by_email(user.email)
        if email_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email Already Used"
            )'''
    username_user = await all_crud.get_user_by_username(user.username)
    if username_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username Already Taken"
        )
    # Hash password and create user
    user.hashed_password = get_password_hash(user.hashed_password)
    new_user = await all_crud.create_user(user_data=user)
    if not new_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User could not be created"
        )
    # Automatically create a blank profile for the new user.
    profile_data = UserProfileCreate(
        user_id=new_user["_id"],
        major=None,
        year=None,
        interests=[],
        badges=[],
        personality_type=None
    )
    profile_dict = profile_data.model_dump(by_alias=True)
    profile_dict["profile_created_at"] = datetime.utcnow()
    new_profile = await all_crud.create_profile(profile_dict)
    if not new_profile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User created, but profile creation failed"
        )
    return {"status": "Account and Profile Created Successfully"}


@router.get("/user/me")
async def read_user_info(
    current_user: Annotated[UserAuth, Depends(get_current_active_user)]
):
    user_info = await all_crud.get_user_by_username(current_user.username)
    return user_info


# ---------------------------
# Profile Endpoints
# ---------------------------
@router.get("/profiles/me", response_model=UserProfileDB)
async def get_my_profile(
    current_user: Annotated[UserAuth, Depends(get_current_active_user)]
):
    profile = await all_crud.get_profile_by_user_id(str(current_user.id))
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


@router.put("/profiles/me", response_model=UserProfileDB)
async def update_my_profile(
    profile_data: UserProfileCreate,
    current_user: Annotated[UserAuth, Depends(get_current_active_user)]
):
    # Ignore any user_id in profile_data; use current_user.id instead.
    update_dict = profile_data.model_dump(by_alias=True)
    update_dict["user_id"] = current_user.id  # enforce current user's id
    update_dict["profile_created_at"] = datetime.utcnow()
    updated = await all_crud.update_profile(str(current_user.id), update_dict)
    if not updated:
        raise HTTPException(
            status_code=404, detail="Profile not found or update failed")
    return updated


# ---------------------------
# Event Endpoints
# ---------------------------
@router.post("/events", response_model=EventDB)
async def create_event_endpoint(
    event: EventCreate,
    current_user: Annotated[UserAuth, Depends(get_current_active_user)]
):
    event_dict = event.model_dump()
    event_dict["created_at"] = datetime.utcnow()
    new_event = await all_crud.create_event(event_dict)
    if not new_event:
        raise HTTPException(status_code=400, detail="Could not create event")
    return new_event


@router.get("/events", response_model=List[EventDB])
async def list_events():
    events = await all_crud.get_all_events()
    return events


@router.get("/events/{event_id}", response_model=EventDB)
async def get_event_endpoint(event_id: str):
    event = await all_crud.get_event_by_id(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return event


@router.put("/events/{event_id}", response_model=EventDB)
async def update_event_endpoint(
    event_id: str,
    event: EventCreate,
    current_user: Annotated[UserAuth, Depends(get_current_active_user)]
):
    event_dict = event.model_dump()
    event_dict["created_at"] = datetime.utcnow()
    updated_event = await all_crud.update_event(event_id, event_dict)
    if not updated_event:
        raise HTTPException(
            status_code=404, detail="Event not found or update failed")
    return updated_event


@router.delete("/events/{event_id}")
async def delete_event_endpoint(
    event_id: str,
    current_user: Annotated[UserAuth, Depends(get_current_active_user)]
):
    success = await all_crud.delete_event(event_id)
    if not success:
        raise HTTPException(
            status_code=404, detail="Event not found or delete failed")
    return {"detail": "Event deleted"}

# ---------------------------
# Attendance Endpoints
# ---------------------------


@router.post("/attendance", response_model=AttendanceDB)
async def record_attendance(
    att: AttendanceCreate,
    current_user: Annotated[UserAuth, Depends(get_current_active_user)]
):
    # Use current_user.id instead of relying on the incoming payload
    att_dict = att.model_dump()
    att_dict["user_id"] = current_user.id
    if not att_dict.get("scanned_at"):
        att_dict["scanned_at"] = datetime.utcnow()
    new_att = await all_crud.create_attendance(att_dict)
    if not new_att:
        raise HTTPException(
            status_code=400, detail="Could not record attendance")
    return new_att


@router.get("/attendance", response_model=List[AttendanceDB])
async def list_attendance(
    user_id: Optional[str] = Query(None),
    event_id: Optional[str] = Query(None)
):
    attendances = await all_crud.find_attendances(user_id, event_id)
    return attendances


####
# AI API
@router.get("/ai/summary/{event_id}", response_model=AISummaryDB)
async def get_ai_summary_for_event(event_id: str):
    """
    Retrieve the latest AI summary record for the given event_id.
    No authentication is required.

    :param event_id: The event's ID as a string.
    :return: A JSON object of the AI summary (with ObjectId fields converted to strings).
    """
    summary = await all_crud.get_latest_ai_summary_by_event(event_id)
    if not summary:
        raise HTTPException(
            status_code=404, detail="No AI summary found for this event")
    return summary


@router.post("/ai/request/{event_id}", response_model=AISummaryDB)
async def create_ai_summary_for_event(event_id: str):
    """
    Generate and save an AI summary record for the given event by invoking the AI integration logic.
    This endpoint calls the LLM to generate sentiment analysis and event recommendations based on user personas,
    then saves the prompt and LLM response to the database.

    :param event_id: The event's ID as a string.
    :return: The saved AI summary record as a JSON object (with ObjectId fields converted to strings).
    """
    try:
        result = await generate_recommendation(event_id)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"AI summarization failed: {e}")

    if not result.get("saved_record"):
        raise HTTPException(
            status_code=500, detail="Failed to save AI summary record.")

    return result["saved_record"]
