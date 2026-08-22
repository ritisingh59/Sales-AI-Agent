import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from project root
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

class Settings:
    PROJECT_NAME: str = "Northstar Homes AI Agent"
    VERSION: str = "1.0.0"
    
    # LLM Settings
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    
    # Server Settings
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # Project specific real estate ground truth
    COMPANY_NAME: str = "Northstar Homes"
    PROJECT_TITLE: str = "Northstar One"
    PROJECT_LOCATION: str = "Sector 79, Gurugram"
    CONFIG_2BHK_PRICE: str = "₹1.35 Crore onwards"
    CONFIG_3BHK_PRICE: str = "₹1.75 Crore onwards"

settings = Settings()
