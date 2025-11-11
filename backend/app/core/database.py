from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.models.user import User
from app.models.plate_detection import PlateDetection
from app.core.config import settings

client = None
db = None

async def init_db():
    """Initialize database connection"""
    global client, db
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client[settings.DATABASE_NAME]
    
    await init_beanie(
        database=db,
        document_models=[User, PlateDetection]
    )

async def close_db():
    """Close database connection"""
    global client
    if client:
        client.close()

def get_database():
    """Get database instance"""
    return db
