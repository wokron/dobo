from pathlib import Path
from typing import Any, Tuple, Type

import dotenv
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    TomlConfigSettingsSource,
)

dotenv.load_dotenv(".env")

DEFAULT_DATABASE_FILE = "database.db"
DEFAULT_MEMORY_FILE = "memory.db"


class EmbeddingsSettings(BaseSettings):
    type: str = "DeterministicFakeEmbedding"
    config: dict[str, Any] = {"size": 256}


class LLMSettings(BaseSettings):
    type: str = "FakeListChatModel"
    config: dict[str, Any] = {"responses": ["I don't know"]}


class ChainSettings(BaseSettings):
    verbose: bool = False
    debug: bool = False


class Settings(BaseSettings):
    model_config = SettingsConfigDict(toml_file="config.toml")

    database_url: str = f"sqlite:///{DEFAULT_DATABASE_FILE}"
    memory_url: str = f"sqlite:///{DEFAULT_MEMORY_FILE}"
    data_dir: Path = "./data"

    llm: LLMSettings = LLMSettings()
    embeddings: EmbeddingsSettings = EmbeddingsSettings()
    chain: ChainSettings = ChainSettings()

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
