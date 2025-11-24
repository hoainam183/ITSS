from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MONGODB_URL: str
    SECRET_KEY: str
    PROJECT_NAME: str = "Insight Bridge API"

    class Config:
        env_file = ".env"

settings = Settings()