from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "OpsPulse API"
    app_version: str = "1.0.0"
    database_url: str = "postgresql+psycopg://opspulse:opspulse@localhost:5432/opspulse"
    debug: bool = False

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
