from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_prefix="INDUSTRIAL_AI_", extra="ignore")

    app_name: str = "Industrial AI Knowledge Assistant"
    api_prefix: str = "/api/v1"
    data_dir: Path = Path("data")
    database_path: Path = Path("data/industrial_ai.db")
    upload_dir: Path = Path("data/raw")
    chunk_size: int = 800
    chunk_overlap: int = 100
    retrieval_top_k: int = 5
    llm_base_url: str | None = None
    llm_api_key: str = ""
    llm_model: str = "deepseek-v4-flash"

    def prepare_directories(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.upload_dir.mkdir(parents=True, exist_ok=True)


@lru_cache
def get_settings() -> Settings:
    return Settings()
