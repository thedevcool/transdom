from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from config import MONGODB_URI, DB_NAME

client: AsyncIOMotorClient = None # pyright: ignore[reportInvalidTypeForm]
db: AsyncIOMotorDatabase = None # pyright: ignore[reportInvalidTypeForm]

async def connect_to_mongo():
    """Connect to MongoDB"""
    global client, db
    client = AsyncIOMotorClient(MONGODB_URI)
    db = client[DB_NAME]
    print(f"✓ Connected to MongoDB: {DB_NAME}")

async def close_mongo_connection():
    """Close MongoDB connection"""
    global client
    if client:
        client.close()
        print("✓ Disconnected from MongoDB")

def get_db() -> AsyncIOMotorDatabase:
    """Get database instance"""
    return db
