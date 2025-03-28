from mongodb import database
from all_model import (
    UserProfileCreate, UserProfileDB,
    EventCreate, EventDB,
    ClubCreate, ClubDB,
    AttendanceCreate, AttendanceDB,
    MembershipCreate, MembershipDB,
    FeedbackCreate, FeedbackDB,
    ResourceCreate, ResourceDB
)
from user_model import UserForm, UserAuth, UserAuthPass
from bson.objectid import ObjectId
from datetime import datetime
from typing import List, Optional

# ---------------------------
# Users CRUD
# ---------------------------
user_collection = database.users


async def get_user(user_id: str) -> UserAuth:
    result = await user_collection.find_one({"_id": ObjectId(user_id)})
    if not result:
        return False
    return UserAuth(**result)


async def get_user_by_username(username: str) -> UserAuthPass:
    result = await user_collection.find_one({"username": username})
    if not result:
        return False
    return UserAuthPass(**result)


async def get_user_by_email(email: str) -> UserAuthPass:
    result = await user_collection.find_one({"email": email})
    if not result:
        return False
    return UserAuthPass(**result)


async def create_user(user_data: UserForm):
    # Use by_alias=True to ensure keys match Mongo's schema (i.e. "_id")
    user_dict = user_data.model_dump(by_alias=True)
    result = await user_collection.insert_one(user_dict)
    new_user = await user_collection.find_one({"_id": result.inserted_id})
    return new_user

# ---------------------------
# User Profiles CRUD
# ---------------------------
profile_collection = database.user_profiles


async def get_profile_by_user_id(user_id: str) -> UserProfileDB:
    result = await profile_collection.find_one({"user_id": ObjectId(user_id)})
    if not result:
        return False
    return UserProfileDB(**result)


async def create_profile(profile_data: dict) -> UserProfileDB:
    # profile_data should include the required "profile_created_at" field.
    result = await profile_collection.insert_one(profile_data)
    new_profile = await profile_collection.find_one({"_id": result.inserted_id})
    return UserProfileDB(**new_profile)


async def update_profile(user_id: str, profile_data: dict) -> UserProfileDB:
    result = await profile_collection.update_one(
        {"user_id": ObjectId(user_id)},
        {"$set": profile_data}
    )
    if result.modified_count == 0:
        return False
    updated = await profile_collection.find_one({"user_id": ObjectId(user_id)})
    return UserProfileDB(**updated)

# ---------------------------
# Events CRUD
# ---------------------------
event_collection = database.events


async def create_event(event_data: dict) -> EventDB:
    result = await event_collection.insert_one(event_data)
    new_event = await event_collection.find_one({"_id": result.inserted_id})
    return EventDB(**new_event)


async def get_all_events() -> List[EventDB]:
    cursor = event_collection.find({})
    events = await cursor.to_list(length=1000)
    return [EventDB(**event) for event in events]


async def get_event_by_id(event_id: str) -> EventDB:
    result = await event_collection.find_one({"_id": ObjectId(event_id)})
    if not result:
        return False
    return EventDB(**result)


async def update_event(event_id: str, event_data: dict) -> EventDB:
    result = await event_collection.update_one(
        {"_id": ObjectId(event_id)},
        {"$set": event_data}
    )
    if result.modified_count == 0:
        return False
    updated = await event_collection.find_one({"_id": ObjectId(event_id)})
    return EventDB(**updated)


async def delete_event(event_id: str) -> bool:
    result = await event_collection.delete_one({"_id": ObjectId(event_id)})
    return result.deleted_count == 1

# ---------------------------
# Clubs CRUD
# ---------------------------
club_collection = database.clubs


async def create_club(club_data: dict) -> ClubDB:
    result = await club_collection.insert_one(club_data)
    new_club = await club_collection.find_one({"_id": result.inserted_id})
    return ClubDB(**new_club)


async def get_all_clubs() -> List[ClubDB]:
    cursor = club_collection.find({})
    clubs = await cursor.to_list(length=1000)
    return [ClubDB(**club) for club in clubs]


async def get_club_by_id(club_id: str) -> ClubDB:
    result = await club_collection.find_one({"_id": ObjectId(club_id)})
    if not result:
        return False
    return ClubDB(**result)


async def update_club(club_id: str, club_data: dict) -> ClubDB:
    result = await club_collection.update_one(
        {"_id": ObjectId(club_id)},
        {"$set": club_data}
    )
    if result.modified_count == 0:
        return False
    updated = await club_collection.find_one({"_id": ObjectId(club_id)})
    return ClubDB(**updated)


async def delete_club(club_id: str) -> bool:
    result = await club_collection.delete_one({"_id": ObjectId(club_id)})
    return result.deleted_count == 1

# ---------------------------
# Attendances CRUD
# ---------------------------
attendance_collection = database.attendances


async def create_attendance(att_data: dict) -> AttendanceDB:
    result = await attendance_collection.insert_one(att_data)
    new_att = await attendance_collection.find_one({"_id": result.inserted_id})
    return AttendanceDB(**new_att)


async def find_attendances(user_id: Optional[str] = None, event_id: Optional[str] = None) -> List[AttendanceDB]:
    query = {}
    if user_id:
        query["user_id"] = ObjectId(user_id)
    if event_id:
        query["event_id"] = ObjectId(event_id)
    cursor = attendance_collection.find(query)
    attendances = await cursor.to_list(length=1000)
    return [AttendanceDB(**att) for att in attendances]

# ---------------------------
# Memberships CRUD
# ---------------------------
membership_collection = database.memberships


async def create_membership(memb_data: dict) -> MembershipDB:
    result = await membership_collection.insert_one(memb_data)
    new_memb = await membership_collection.find_one({"_id": result.inserted_id})
    return MembershipDB(**new_memb)


async def find_memberships(user_id: Optional[str] = None, club_id: Optional[str] = None) -> List[MembershipDB]:
    query = {}
    if user_id:
        query["user_id"] = ObjectId(user_id)
    if club_id:
        query["club_id"] = ObjectId(club_id)
    cursor = membership_collection.find(query)
    memberships = await cursor.to_list(length=1000)
    return [MembershipDB(**memb) for memb in memberships]

# ---------------------------
# Feedback CRUD
# ---------------------------
feedback_collection = database.feedback


async def create_feedback(fb_data: dict) -> FeedbackDB:
    result = await feedback_collection.insert_one(fb_data)
    new_fb = await feedback_collection.find_one({"_id": result.inserted_id})
    return FeedbackDB(**new_fb)


async def find_feedback(target_type: Optional[str] = None, target_id: Optional[str] = None) -> List[FeedbackDB]:
    query = {}
    if target_type:
        query["target_type"] = target_type
    if target_id:
        query["target_id"] = ObjectId(target_id)
    cursor = feedback_collection.find(query)
    feedbacks = await cursor.to_list(length=1000)
    return [FeedbackDB(**fb) for fb in feedbacks]

# ---------------------------
# Resources CRUD
# ---------------------------
resource_collection = database.resources


async def create_resource(res_data: dict) -> ResourceDB:
    result = await resource_collection.insert_one(res_data)
    new_res = await resource_collection.find_one({"_id": result.inserted_id})
    return ResourceDB(**new_res)


async def get_all_resources() -> List[ResourceDB]:
    cursor = resource_collection.find({})
    resources = await cursor.to_list(length=1000)
    return [ResourceDB(**res) for res in resources]


async def get_resource_by_id(res_id: str) -> ResourceDB:
    result = await resource_collection.find_one({"_id": ObjectId(res_id)})
    if not result:
        return False
    return ResourceDB(**result)


async def update_resource(res_id: str, res_data: dict) -> ResourceDB:
    result = await resource_collection.update_one(
        {"_id": ObjectId(res_id)},
        {"$set": res_data}
    )
    if result.modified_count == 0:
        return False
    updated = await resource_collection.find_one({"_id": ObjectId(res_id)})
    return ResourceDB(**updated)


async def delete_resource(res_id: str) -> bool:
    result = await resource_collection.delete_one({"_id": ObjectId(res_id)})
    return result.deleted_count == 1
