import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

class Settings:
    PROJECT_NAME: str = "Shivar - Agricultural Marketplace (शिवार - कृषी बाजारपेठ)"
    PROJECT_DESCRIPTION: str = "Multi-language e-commerce platform for farmers"
    VERSION: str = "1.0.0"
    
    # Owner & Contact Details
    OWNER_NAME: str = os.getenv("OWNER_NAME", "Shivar Krushi Seva Kendra")
    OWNER_PHONE: str = os.getenv("OWNER_PHONE", "9021273002")
    OWNER_WHATSAPP: str = os.getenv("OWNER_WHATSAPP", "9021273002")
    OWNER_EMAIL: str = os.getenv("OWNER_EMAIL", "support@shivar.com")
    STORE_LOCATION: str = os.getenv("STORE_LOCATION", "Maharashtra, India")
    
    # Admin Credentials
    ADMIN_USERNAME: str = os.getenv("ADMIN_USERNAME", "admin@shivar.com")
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "shivar@2026")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "shivar-secret-super-secure-key-2026-agri-mart")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR}/shivar.db")
    
    # Currency & Localization
    CURRENCY_SYMBOL: str = "₹"
    CURRENCY_CODE: str = "INR"
    SUPPORTED_LANGUAGES: list[str] = ["mr", "hi", "en"]
    DEFAULT_LANGUAGE: str = "mr"  # Default Marathi for Maharashtra farmers

settings = Settings()
