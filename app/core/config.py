# app/core/config.py
import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv
from typing import List, Optional

# Load environment variables
load_dotenv()

class Settings(BaseSettings):
    """Application settings configuration"""
    
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "IIT Chicago AI Enrollment Assistant"
    
    # CORS Settings
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:8000", "http://localhost:3000"]
    
    # Authentication
    SECRET_KEY: str = os.getenv("SECRET_KEY", "development_secret_key")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CRM Settings
    SLATE_URL: str = os.getenv("SLATE_URL", "https://apply.illinoistech.edu/manage/inbox/")
    SLATE_USERNAME: str = os.getenv("SLATE_USERNAME", "")
    SLATE_PASSWORD: str = os.getenv("SLATE_PASSWORD", "")
    
    # Voice Settings
    WAKE_WORD: str = "Hey Claude"
    VOICE_ENABLED: bool = True
    
    # Browser Automation
    BROWSER_HEADLESS: bool = False  # Set to True in production
    BROWSER_TYPE: str = "chromium"  # chromium, firefox, webkit
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # OpenAI Settings
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4o")
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Initialize settings
settings = Settings()