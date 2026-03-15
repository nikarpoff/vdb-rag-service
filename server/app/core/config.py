from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    weaviate_url: str = "http://weaviate:8080"
    docling_url: str = "http://docling:8501"
    weaviate_grpc_url: str = "weaviate:50051"
    llm_api_key: Optional[str] = None
    llm_model: str = "gpt-4"
    llm_base_url: Optional[str] = None
    llm_external_endpoint: Optional[str] = None
    llm_timeout_seconds: float = 30.0
    embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2"
    embedding_batch_size: int = 32

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "allow"


settings = Settings()
