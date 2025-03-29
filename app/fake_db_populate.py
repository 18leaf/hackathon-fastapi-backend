import asyncio
import random
from datetime import datetime, timedelta
from all_crud import (
    create_user, create_profile, create_event, create_attendance
)
from user_model import UserForm

# Increase variability by expanding the sample data sets
majors = [
    "Computer Science", "Engineering", "Mathematics", "Biology",
    "History", "Psychology", "Philosophy", "Art", "Economics", "Physics"
]
years = [1, 2, 3, 4, 5]
interests_list = [
    ["AI", "Networking", "Data Science"],
    ["Robotics", "Sports", "Entrepreneurship"],
    ["Literature", "Philosophy", "Creative Writing"],
    ["Music", "Art", "Theater"],
    ["Economics", "Business", "Marketing"],
    ["Coding", "Gaming", "Hiking"],
    ["Social Media", "Volunteering", "Cooking"],
]
# Make "None" more likely by repeating it.
special_conditions = [
    "None", "None", "None", "None", "None", "wheelchair user",
    "visually impaired", "deaf", "anxiety", "ADHD"
]
# Additional interests to add when a special condition is present
additional_interests = ["Accessibility", "Inclusive Design", "Assistive Tech"]


async def populate_users(num_users: int = 15) -> list:
    """
    Create test users with unique usernames and emails.
    """
    users = []
    for i in range(num_users):
        user = UserForm(
            email=f"user{i}@example.com",
            username=f"user{i}",
            name=f"User {i}",
            hashed_password="dummy_password"  # to be hashed by create_user()
        )
        new_user = await create_user(user_data=user)
        users.append(new_user)
        print(f"Created user: {new_user['username']} (ID: {new_user['_id']})")
    return users


async def populate_profiles(users: list):
    """
    Create a profile for each user with diverse attributes.
    If a user gets a special condition (other than 'None'),
    append additional interests to their interests array.
    """
    for user in users:
        base_interests = random.choice(interests_list).copy()
        chosen_condition = random.choice(special_conditions)
        # If there's a special condition other than "None", append additional interest
        if chosen_condition != "None":
            base_interests += random.sample(additional_interests,
                                            k=random.randint(1, len(additional_interests)))
        profile_data = {
            "user_id": user["_id"],
            "major": random.choice(majors),
            "year": random.choice(years),
            "interests": base_interests,
            "badges": [],
            "personality_type": random.choice([
                "Introvert", "Extrovert", "Ambivert", "Neurodiverse", "Creative",
                "Analytical", "Empathetic", "Pragmatic", "Innovative", "Reserved", "Outgoing"
            ]),
            "profile_created_at": datetime.utcnow()
        }
        new_profile = await create_profile(profile_data)
        print(
            f"Created profile for user {user['username']} (Profile ID: {new_profile.id})")


async def populate_events() -> list:
    """
    Create several events with variability in dates and locations.
    """
    base_event_names = [
        "Hackathon Kickoff",
        "Networking Lunch",
        "Tech Workshop"
    ]
    locations = ["Auditorium", "Cafeteria", "Room 101", "Main Hall", "Online"]
    events = []
    for name in base_event_names:
        # Randomly offset the event date by up to +/-5 days
        event_date = datetime.utcnow() + timedelta(days=random.randint(-5, 5))
        event_data = {
            "name": name,
            "description": f"{name} event designed to stimulate collaboration and creativity.",
            "date": event_date.isoformat(),
            "location": random.choice(locations),
            "tags": [name.lower().replace(" ", "_"), "test"],
            "created_at": datetime.utcnow().isoformat()
        }
        event = await create_event(event_data)
        events.append(event)
        print(f"Created event: {event.name} (ID: {event.id})")
    return events


async def populate_attendances(events: list, users: list):
    """
    For each event, randomly select a subset of users as attendees.
    Additionally, randomly add feedback to some attendances.
    """
    feedback_options = [
        {"rating": 5, "comment": "Excellent event!"},
        {"rating": 4, "comment": "Very engaging and fun."},
        {"rating": 3, "comment": "It was okay, could be improved."},
        {"rating": 2, "comment": "Not very well organized."},
        {"rating": 1, "comment": "Poor experience."}
    ]
    for event in events:
        num_attendees = random.randint(5, len(users))
        attending_users = random.sample(users, num_attendees)
        for user in attending_users:
            feedback = random.choice(
                feedback_options) if random.random() < 0.4 else None
            att_data = {
                "user_id": user["_id"],
                "event_id": event.model_dump(by_alias=True)["_id"],
                "scanned_at": datetime.utcnow().isoformat(),
                "feedback": feedback,
            }
            new_att = await create_attendance(att_data)
        print(
            f"Recorded attendance for event: {event.name} with {num_attendees} attendees.")


async def main():
    print("Populating database with test data...")
    users = await populate_users(15)
    await populate_profiles(users)
    events = await populate_events()
    await populate_attendances(events, users)
    print("Database population complete.")

if __name__ == "__main__":
    asyncio.run(main())
