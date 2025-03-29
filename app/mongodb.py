from motor.motor_asyncio import AsyncIOMotorClient
from config import settings

client = AsyncIOMotorClient(settings.MONGO_URI)
# change clinet.(name) for
# use HACKATHONFAKED for AI integrations
database = client.HACKATHONDB
