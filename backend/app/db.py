from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.config import settings

class Database:
    client: AsyncIOMotorClient = None
    db: AsyncIOMotorDatabase = None

db_instance = Database()

async def connect_to_mongo():
    db_instance.client = AsyncIOMotorClient(settings.MONGO_URI)
    db_instance.db = db_instance.client[settings.MONGO_DB_NAME]
    
    # Ensure indexes
    db = db_instance.db
    await db.users.create_index("email", unique=True)
    await db.subjects.create_index("user_id")
    await db.topics.create_index([("user_id", 1), ("subject_id", 1)])
    await db.events.create_index([("user_id", 1), ("due_date", 1)])
    await db.availability.create_index("user_id", unique=True)
    await db.sessions.create_index([("user_id", 1), ("planned_date", 1)])
    await db.questions.create_index([("topic_id", 1)])
    await db.quiz_attempts.create_index([("user_id", 1), ("topic_id", 1)])

async def close_mongo_connection():
    if db_instance.client:
        db_instance.client.close()

def get_db() -> AsyncIOMotorDatabase:
    if db_instance.db is None:
        db_instance.client = AsyncIOMotorClient(settings.MONGO_URI)
        db_instance.db = db_instance.client[settings.MONGO_DB_NAME]
    return db_instance.db
