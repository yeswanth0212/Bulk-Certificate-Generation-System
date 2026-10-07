import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    PROJECT_NAME: str = "Bulk Certificate Generator API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR}/certificates.db")
    
    # Certificate Generation & Storage
    OUTPUT_DIR: Path = BASE_DIR / "generated_certificates"
    BASE_URL: str = os.getenv("BASE_URL", "http://localhost:8000")
    
    # Design / Default parameters
    DEFAULT_ISSUER_NAME: str = "Global Learning & Training Academy"
    DEFAULT_COURSE_TITLE: str = "Certificate of Excellence"

    model_config = SettingsConfigDict(case_sensitive=True)


settings = Settings()

# Ensure output directory exists
settings.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
