import logging
from pathlib import Path
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict
from openai import OpenAI

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=(".env", "../.env"), extra="ignore")

    openai_api_key: str
    model_name: str = "gpt-4o-mini"
    model_temperature: float = 0.0

    database_url: str = "postgresql://postgres:postgres@localhost:5432/analytics"

    chroma_persist_dir: str = "./chroma_data"
    chunk_size: int = 1000
    chunk_overlap: int = 200

    upload_dir: str = "./uploads"
    max_query_rows: int = 500
    sql_timeout_seconds: int = 30


@lru_cache
def get_settings() -> Settings:
    return Settings()


@lru_cache
def get_openai_client() -> OpenAI:
    return OpenAI(api_key=get_settings().openai_api_key)
