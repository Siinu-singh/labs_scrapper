import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Lab Test Scraper API"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    CHROME_BINARY_LOCATION: str = "/usr/bin/chromium-browser"
    CHROMEDRIVER_PATH: str = "/usr/bin/chromedriver"
    
    # Database URL from environment variable (PostgreSQL by default)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://localhost/lab_scraper_db")
    DATABASE_ECHO: bool = False
    
    class Config:
        env_file = ".env"

settings = Settings()
