import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    mongodb_url: str = os.getenv("MONGODB_URL", "mongodb+srv://session:session@session.fhqescw.mongodb.net/")
    database_name: str = os.getenv("DATABASE_NAME", "session_tracker")
    
    # Collections
    page_tracks_collection: str = "page_tracks"
    sessions_collection: str = "sessions"
    
    # JWT Settings
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-this-in-production")
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

settings = Settings() 