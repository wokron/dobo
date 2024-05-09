import os
from pathlib import Path
from typing import Any, Tuple, Type

import dotenv
from pydantic import Field
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    TomlConfigSettingsSource,
)

ENV_PATH = os.environ.get("DOBO_ENV_PATH", ".env")

dotenv.load_dotenv(ENV_PATH)

CONFIG_PATH: str = os.environ.get("DOBO_CONFIG_PATH", "config.toml")


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


class VectorStoreSettings(BaseSettings):
    score_threshold: float = Field(0.8, ge=0, le=1)
    history_aware: bool = True
    top_k: int = Field(4, gt=0)



class Settings(BaseSettings):
    model_config = SettingsConfigDict(toml_file=CONFIG_PATH)

    database_url: str = f"sqlite:///{DEFAULT_DATABASE_FILE}"
    memory_url: str = f"sqlite:///{DEFAULT_MEMORY_FILE}"
    data_dir: Path = "./data"

    llm: LLMSettings = LLMSettings()
    embeddings: EmbeddingsSettings = EmbeddingsSettings()
    chain: ChainSettings = ChainSettings()
    vectorstore: VectorStoreSettings = VectorStoreSettings()

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
