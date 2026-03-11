from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    mongo_url: str = "mongodb://manup:manup_secret@mongodb:27017/"
    mongo_db: str = "manup"
    jwt_secret: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    openai_api_key: str = "sk-placeholder"
    mixpanel_token: str = "placeholder"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()
