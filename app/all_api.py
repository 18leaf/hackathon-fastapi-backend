from datetime import datetime
from typing import Annotated, Optional, List
from fastapi import APIRouter, HTTPException, status, Depends, Query
from user_model import UserForm, UserAuth
from all_model import (
    UserProfileCreate, UserProfileDB,
    EventCreate, EventDB,
    ClubCreate, ClubDB,
    AttendanceCreate, AttendanceDB,
    MembershipCreate, MembershipDB,
    FeedbackCreate, FeedbackDB,
    ResourceCreate, ResourceDB
)
import all_crud
from authentication import get_password_hash, get_current_active_user

router = APIRouter()

# ---------------------------
# User Endpoints (Composite)
# ---------------------------


@router.post("/user/create_user")
async def create_user_endpoint(user: UserForm):
    # Validate uniqueness
    if user.email:
        email_user = await all_crud.get_user_by_email(user.email)
        if email_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email Already Used"
            )
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
    # Since our UserProfileDB model requires a 'profile_created_at' field,
    # we manually inject it here.
    profile_data = UserProfileCreate(
        user_id=new_user["_id"],
        major=None,
        year=None,
        interests=[],
        badges=[],
        personality_type=None
    )
    # Convert to dict and inject the required timestamp.
    profile_dict = profile_data.model_dump()
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
    if str(current_user.id) != str(profile_data.user_id):
        raise HTTPException(status_code=403, detail="User ID mismatch")
    # Inject current timestamp if needed (or use provided value)
    update_dict = profile_data.model_dump()
    # In our model, 'profile_created_at' is required for DB output.
    # You might want to leave the original timestamp unchanged or update it.
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
    # Before inserting, inject the required 'created_at'
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
# Club Endpoints
# ---------------------------
@router.post("/clubs", response_model=ClubDB)
async def create_club_endpoint(
    club: ClubCreate,
    current_user: Annotated[UserAuth, Depends(get_current_active_user)]
):
    club_dict = club.model_dump()
    club_dict["created_at"] = datetime.utcnow()
    new_club = await all_crud.create_club(club_dict)
    if not new_club:
        raise HTTPException(status_code=400, detail="Could not create club")
    return new_club


@router.get("/clubs", response_model=List[ClubDB])
async def list_clubs():
    clubs = await all_crud.get_all_clubs()
    return clubs


@router.get("/clubs/{club_id}", response_model=ClubDB)
async def get_club_endpoint(club_id: str):
    club = await all_crud.get_club_by_id(club_id)
    if not club:
        raise HTTPException(status_code=404, detail="Club not found")
    return club


@router.put("/clubs/{club_id}", response_model=ClubDB)
async def update_club_endpoint(
    club_id: str,
    club: ClubCreate,
    current_user: Annotated[UserAuth, Depends(get_current_active_user)]
):
    club_dict = club.model_dump()
    club_dict["created_at"] = datetime.utcnow()
    updated_club = await all_crud.update_club(club_id, club_dict)
    if not updated_club:
        raise HTTPException(
            status_code=404, detail="Club not found or update failed")
    return updated_club


@router.delete("/clubs/{club_id}")
async def delete_club_endpoint(
    club_id: str,
    current_user: Annotated[UserAuth, Depends(get_current_active_user)]
):
    success = await all_crud.delete_club(club_id)
    if not success:
        raise HTTPException(
            status_code=404, detail="Club not found or delete failed")
    return {"detail": "Club deleted"}


# ---------------------------
# Attendance Endpoints
# ---------------------------
@router.post("/attendance", response_model=AttendanceDB)
async def record_attendance(
    att: AttendanceCreate,
    current_user: Annotated[UserAuth, Depends(get_current_active_user)]
):
    if str(current_user.id) != str(att.user_id):
        raise HTTPException(status_code=403, detail="User ID mismatch")
    # If 'scanned_at' is missing, add the current timestamp.
    att_dict = att.model_dump()
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


# ---------------------------
# Membership Endpoints
# ---------------------------
@router.post("/membership", response_model=MembershipDB)
async def join_membership(
    memb: MembershipCreate,
    current_user: Annotated[UserAuth, Depends(get_current_active_user)]
):
    if str(current_user.id) != str(memb.user_id):
        raise HTTPException(status_code=403, detail="User ID mismatch")
    memb_dict = memb.model_dump()
    if not memb_dict.get("joined_at"):
        memb_dict["joined_at"] = datetime.utcnow()
    new_memb = await all_crud.create_membership(memb_dict)
    if not new_memb:
        raise HTTPException(
            status_code=400, detail="Could not join membership")
    return new_memb


@router.get("/membership", response_model=List[MembershipDB])
async def list_memberships(
    user_id: Optional[str] = Query(None),
    club_id: Optional[str] = Query(None)
):
    memberships = await all_crud.find_memberships(user_id, club_id)
    return memberships


# ---------------------------
# Feedback Endpoints
# ---------------------------
@router.post("/feedback", response_model=FeedbackDB)
async def create_feedback_endpoint(
    feedback: FeedbackCreate,
    current_user: Annotated[UserAuth, Depends(get_current_active_user)]
):
    if str(current_user.id) != str(feedback.user_id):
        raise HTTPException(status_code=403, detail="User ID mismatch")
    fb_dict = feedback.model_dump()
    # Ensure required created_at field is present.
    if not fb_dict.get("created_at"):
        fb_dict["created_at"] = datetime.utcnow()
    new_fb = await all_crud.create_feedback(fb_dict)
    if not new_fb:
        raise HTTPException(
            status_code=400, detail="Could not create feedback")
    return new_fb


@router.get("/feedback", response_model=List[FeedbackDB])
async def list_feedback(
    target_type: Optional[str] = Query(None),
    target_id: Optional[str] = Query(None)
):
    feedbacks = await all_crud.find_feedback(target_type, target_id)
    return feedbacks


# ---------------------------
# Resource Endpoints
# ---------------------------
@router.post("/resources", response_model=ResourceDB)
async def create_resource_endpoint(
    resource: ResourceCreate,
    current_user: Annotated[UserAuth, Depends(get_current_active_user)]
):
    res_dict = resource.model_dump()
    new_resource = await all_crud.create_resource(res_dict)
    if not new_resource:
        raise HTTPException(
            status_code=400, detail="Could not create resource")
    return new_resource


@router.get("/resources", response_model=List[ResourceDB])
async def list_resources():
    resources = await all_crud.get_all_resources()
    return resources


@router.get("/resources/{res_id}", response_model=ResourceDB)
async def get_resource_endpoint(res_id: str):
    resource = await all_crud.get_resource_by_id(res_id)
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    return resource


@router.put("/resources/{res_id}", response_model=ResourceDB)
async def update_resource_endpoint(
    res_id: str,
    resource: ResourceCreate,
    current_user: Annotated[UserAuth, Depends(get_current_active_user)]
):
    res_dict = resource.model_dump()
    updated_resource = await all_crud.update_resource(res_id, res_dict)
    if not updated_resource:
        raise HTTPException(
            status_code=404, detail="Resource not found or update failed")
    return updated_resource


@router.delete("/resources/{res_id}")
async def delete_resource_endpoint(
    res_id: str,
    current_user: Annotated[UserAuth, Depends(get_current_active_user)]
):
    success = await all_crud.delete_resource(res_id)
    if not success:
        raise HTTPException(
            status_code=404, detail="Resource not found or delete failed")
    return {"detail": "Resource deleted"}
