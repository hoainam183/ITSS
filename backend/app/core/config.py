from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MONGODB_URL: str
    SECRET_KEY: str
    PROJECT_NAME: str = "Insight Bridge API"

    AI_PROVIDER: str | None = None
    AZURE_OPENAI_API_KEY: str | None = None
    AZURE_OPENAI_ENDPOINT: str | None = None
    AZURE_OPENAI_DEPLOYMENT: str | None = None
    AZURE_OPENAI_API_VERSION: str | None = None
    OPENAI_API_KEY: str | None = None
    OPENAI_BASE_URL: str | None = None
    OPENAI_MODEL: str | None = None

    class Config:
        env_file = ".env"
        extra = "ignore" 
settings = Settings()