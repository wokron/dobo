from typing import Any, Tuple, Type
from pydantic_settings import BaseSettings, SettingsConfigDict

from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    TomlConfigSettingsSource,
)


class LLMSettings(BaseSettings):
    class_name: str = "HumanInputChatModel"
    config: dict[str, Any] = {}


class Settings(BaseSettings):
    database_url: str = "sqlite:///database.db"
    memory_url: str = "sqlite:///memory.db"
    data_dir: str = "./data"

    llm: LLMSettings = LLMSettings()

    model_config = SettingsConfigDict(env_file=".env", toml_file="config.toml")

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            dotenv_settings,
            TomlConfigSettingsSource(settings_cls),
            env_settings,
            file_secret_settings,
        )


settings = Settings()
