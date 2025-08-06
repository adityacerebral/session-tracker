from motor.motor_asyncio import AsyncIOMotorClient
from app.config import settings
import certifi

class Database:
    client: AsyncIOMotorClient = None
    database = None

db = Database()

async def get_database():
    return db.database

async def connect_to_mongo():
    """Create database connection"""
    db.client = AsyncIOMotorClient(
        settings.mongodb_url,
        tlsCAFile=certifi.where()
    )
    db.database = db.client[settings.database_name]
    print("✅ Connected to MongoDB")

async def close_mongo_connection():
    """Close database connection"""
    db.client.close()
    print("❌ Disconnected from MongoDB")
