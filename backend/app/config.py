from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


ROOT_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    app_name: str = "Rafed AI"
    frontend_origin: str = "http://localhost:5173"

    embedding_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    chroma_dir: str = "./backend/data/chroma"
    knowledge_base_dir: str = "./knowledge_base"
    top_k: int = 5
    github_owner: str = "rafazidi"
    github_topic: str = "portfolio"
    github_cache_ttl_seconds: int = 300

    llm_api_key: str = ""
    llm_base_url: str = "https://api.openai.com/v1"
    llm_model: str = ""
    llm_temperature: float = 0.2

    model_config = SettingsConfigDict(
        env_file=ROOT_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def absolute_chroma_dir(self) -> Path:
        path = Path(self.chroma_dir)
        return path if path.is_absolute() else ROOT_DIR / path

    @property
    def absolute_knowledge_base_dir(self) -> Path:
        path = Path(self.knowledge_base_dir)
        return path if path.is_absolute() else ROOT_DIR / path


settings = Settings()
