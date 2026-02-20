from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Lab Test Scraper API"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"  # Changed default to development
    CHROME_BINARY_LOCATION: str = "/usr/bin/chromium-browser"
    CHROMEDRIVER_PATH: str = "/usr/bin/chromedriver"
    
    class Config:
        env_file = ".env"

settings = Settings()
