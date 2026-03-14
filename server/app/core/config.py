from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    weaviate_url: str = "http://weaviate:8080"
    docling_url: str = "http://docling:8501"
    llm_api_key: Optional[str] = None
    llm_model: str = "gpt-4"
    llm_base_url: Optional[str] = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "allow"


settings = Settings()
