from motor.motor_asyncio import AsyncIOMotorClient
from config import settings

client = AsyncIOMotorClient(settings.MONGO_URI)
# change clinet.(name) for
database = client.HACKATHONDB
