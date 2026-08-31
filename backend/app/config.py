import os
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    chroma_persist_dir: str = "./chroma_db"
    sqlite_db_path: str = "./conversations.db"
    default_embedding_model: str = "all-MiniLM-L6-v2"
    langchain_tracing_v2: bool = False
    langchain_endpoint: str = "https://api.smith.langchain.com"
    langchain_api_key: str = ""
    langchain_project: str = "CogniFlow-Agent"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

os.environ.setdefault("LANGCHAIN_TRACING_V2", str(settings.langchain_tracing_v2).lower())
os.environ.setdefault("LANGCHAIN_ENDPOINT", settings.langchain_endpoint)
os.environ.setdefault("LANGCHAIN_API_KEY", settings.langchain_api_key)
os.environ.setdefault("LANGCHAIN_PROJECT", settings.langchain_project)
