from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URI: str = "sqlite:///database.db"
    MEMORY_URL: str = "sqlite:///memory.db"
    DATA_DIR: str = "./data"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
