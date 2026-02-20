from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "Lab Test Scraper API"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"  # Changed default to development
    CHROME_BINARY_LOCATION: str = "/usr/bin/chromium-browser"
    CHROMEDRIVER_PATH: str = "/usr/bin/chromedriver"
    
    # MySQL Database Configuration
    DATABASE_HOST: str = "127.0.0.1"
    DATABASE_PORT: int = 3306
    DATABASE_USER: str = "root"
    DATABASE_PASSWORD: str = "Suraj@24!"
    DATABASE_NAME: str = "scraper_db"
    DATABASE_ECHO: bool = False
    
    @property
    def DATABASE_URL(self) -> str:
        from urllib.parse import quote
        password = quote(self.DATABASE_PASSWORD, safe='')
        return f"mysql+pymysql://{self.DATABASE_USER}:{password}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
    
    class Config:
        env_file = ".env"

settings = Settings()
