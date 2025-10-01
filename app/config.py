# app/config.py
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    google_api_key: str = os.getenv("GOOGLE_API_KEY")
    database_url: str = "sqlite:///./test.db"
    
    class Config:
        env_file = ".env"

settings = Settings()