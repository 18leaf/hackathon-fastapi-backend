from typing import List
from ai_model import AISummaryCreate, AISummaryDB
from mongodb import database
from all_model import (
    UserProfileCreate, UserProfileDB,
    EventCreate, EventDB,
    AttendanceCreate, AttendanceDB,
)
from user_model import UserForm, UserAuth, UserAuthPass
from bson.objectid import ObjectId
from datetime import datetime
from typing import Any, Dict, List, Optional

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

# AI RESOURCE


async def get_event_personas(event_id: str) -> List[Dict[str, Any]]:
    """
    Retrieves descriptive user profiles for all users who attended the given event.
    It uses the attendances table to fetch user IDs linked to the event, then queries 
    user_profiles for each user, returning only the descriptive attributes:
        - major
        - year
        - interests
        - personality_type

    :param event_id: The event's ID as a string.
    :return: A list of dictionaries with the descriptive data.
    """
    # Retrieve attendance records for the specified event.
    attendances = await find_attendances(event_id=event_id)
    # Extract unique user IDs using attribute access.
    user_ids = {str(att.user_id) for att in attendances}

    personas: List[Dict[str, Any]] = []
    for uid in user_ids:
        profile = await get_profile_by_user_id(uid)
        if profile:
            # Construct a persona dictionary using only descriptive fields.
            persona = {
                "major": profile.major,
                "year": profile.year,
                "interests": profile.interests,
                "personality_type": profile.personality_type,
            }
            personas.append(persona)

    return personas


# Create a new collection for AI summaries.
ai_summary_collection = database.ai_summaries


async def create_ai_summary(summary_data: dict) -> AISummaryDB:
    """
    Inserts an AI summary record into the collection and returns the document.
    """
    result = await ai_summary_collection.insert_one(summary_data)
    new_summary = await ai_summary_collection.find_one({"_id": result.inserted_id})
    return AISummaryDB(**new_summary)


async def get_latest_ai_summary_by_event(event_id: str) -> Optional[AISummaryDB]:
    """
    Retrieves the most recent AI summary record for the given event.

    :param event_id: The event's ID as a string.
    :return: An instance of AISummaryDB containing the latest summary, or None if not found.
    """
    query = {"event_id": ObjectId(event_id)}
    # Sort by 'created_at' in descending order to get the most recent record
    document = await ai_summary_collection.find_one(query, sort=[("created_at", -1)])
    if not document:
        return None
    return AISummaryDB(**document)


async def get_ai_summary_by_event(event_id: str) -> List[AISummaryDB]:
    """
    Retrieves all AI summary records for a given event.
    """
    query = {"event_id": ObjectId(event_id)}
    cursor = ai_summary_collection.find_one(query)
    summaries = await cursor.to_list(length=1000)
    return [AISummaryDB(**s) for s in summaries]
