from typing import Optional
from dotenv import load_dotenv
import logging
from pydantic_settings import BaseSettings, SettingsConfigDict
from enum import Enum

load_dotenv()

class Currency(str, Enum):
    RON = "RON"
    EUR = "EUR"
    USD = "USD"
    
class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )
    
    APP_NAME: str = "Budget Tracker"
    DATABASE_URL: Optional[str]
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    TIMEZONE: str
    DEFAULT_CURRENCY: Currency = Currency.RON
    
    @property
    def log_level(self) -> int:
        return getattr(logging, self.LOG_LEVEL.upper(), logging.INFO)
    
    
settings = Settings()

def config_logging() -> None:
    logging.basicConfig(
        level=settings.log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )