from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
from functools import lru_cache

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='allow')
    # API Settings
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    DEBUG: bool = False
    
    # Database Settings
    DATABASE_URL: str = "postgresql://finagent:finagent123@localhost:5432/finagent_db"
    
    # Redis Settings
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # OpenAI Settings
    OPENAI_API_KEY: str = "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"
    
    # Financial API Settings
    ALPHA_VANTAGE_API_KEY: Optional[str] = None
    TWELVE_DATA_API_KEY: Optional[str] = None
    
    # Monitoring Settings
    ENABLE_TELEMETRY: bool = True
    PROMETHEUS_METRICS: bool = True
    
    # Model Settings
    DEFAULT_LLM_MODEL: str = "gpt-4-turbo-preview"
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()

# Constants
SUPPORTED_INTENTS = [
    "explanation",
    "calculation",
    "comparison",
    "prediction",
    "advice"
]

SUPPORTED_DATA_SOURCES = [
    "knowledge_base",
    "market_data",
    "news_feeds",
    "economic_indicators"
]

TIME_RANGES = [
    "1d",  # 1 day
    "1w",  # 1 week
    "1m",  # 1 month
    "1y"   # 1 year
]

# Error Messages
ERROR_MESSAGES = {
    "invalid_intent": "Invalid intent specified. Supported intents: {intents}",
    "invalid_data_source": "Invalid data source specified. Supported sources: {sources}",
    "invalid_time_range": "Invalid time range specified. Supported ranges: {ranges}",
    "api_error": "Error calling external API: {details}",
    "database_error": "Database error occurred: {details}",
    "unauthorized": "Unauthorized access. Please provide valid credentials.",
}
