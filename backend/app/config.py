from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    MONGO_URI: str = "mongodb://localhost:27017"
    MONGO_DB_NAME: str = "study_planner_db"
    JWT_SECRET: str = "super_secret_jwt_key_hackathon_2026_change_in_prod"
    JWT_EXPIRE_MINUTES: int = 10080
    ANTHROPIC_API_KEY: str = ""
    CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000"]

    # Scheduler constants
    DEFAULT_BUFFER_RATIO: float = 0.20  # 20% reserved buffer capacity
    VELOCITY_MIN_CLAMP: float = 0.5
    VELOCITY_MAX_CLAMP: float = 2.5
    MONTE_CARLO_SIMULATIONS: int = 1000

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
