from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    gemini_api_key: str = Field(default="", validation_alias="GEMINI_API_KEY")
    gemini_workout_model: str = Field(default="gemini-2.5-flash", validation_alias="GEMINI_WORKOUT_MODEL")
    gemini_tip_model: str = Field(default="gemini-2.5-flash", validation_alias="GEMINI_TIP_MODEL")
    database_url: str = Field(default="sqlite:///./fitbuddy.db", validation_alias="DATABASE_URL")
    admin_key: str = Field(default="", validation_alias="ADMIN_KEY")

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
